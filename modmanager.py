from __future__ import with_statement
import zipfile,os.path,os,shutil,random,math
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

def my_move(src,dst):
    listOfFiles = os.listdir(src)
    for f in listOfFiles:
        fullPath = src + "/" + f
        os.system ("mv"+ " " + fullPath + " " + dst + "/" + f)

IS_BLANK = 0
IS_MOD = 1
IS_MODPACK = 2
NOTICE = 0
WARNING = 1

class CheckResult:
    file = ""
    safe = 0
    def __init__(self,newzip,safe):
        self.file = newzip
        self.safe = safe

class ModManager:
    errormsg = 0
    error = 0
    report = []
    # Helper functions
    def __init__(self,workingdir):
        self.clear()
        self.wd = workingdir
        
    def clear(self):
        self.report = []
    
    def get_immediate_subdirectories(self,dir):
        return [name for name in os.listdir(dir)
                if os.path.isdir(os.path.join(dir, name))]
    def unzip(self,source_filename, dest_dir):
        zip = zipfile.ZipFile(source_filename)
        zip.extractall(dest_dir)
        
    def zipdir(self,basedir, archivename):
        assert os.path.isdir(basedir)
        with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
            for root, dirs, files in os.walk(basedir):
                #NOTE: ignore empty directories
                for fn in files:
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                    z.write(absfn, zfn)
        
    def _msg(self,title,msg,level=0):
        tmp = ""

        tmp += title
        if msg!="":
            tmp += ": "+msg
            
        if (level == WARNING):
            print("[WARNING] "+tmp)
        else:
            print(tmp)
            
        self.report.append([title,msg,level])
        
    def reportHTML(self):
        res = ""
        for r in self.report:
            if (r[2]==WARNING):
                res += "[WARNING] "
            res += r[0]
            if (r[1]!=""):
                res += ": "+r[1]
            res += "<br>\n"
        return res
    
    # Processes the uploaded zip file
    def run(self,location,title,name,desc,image):
        self._msg("Processing zipped mod",location)
        if not os.path.isfile(location):
            print("Unable to find zip");
            return False
        if not os.path.exists(self.wd):
            os.makedirs(self.wd)
        if os.path.exists(self.wd+"/"+name):
            shutil.rmtree(self.wd+"/"+name)
        os.makedirs(self.wd+"/"+name)
            
        self._msg("Unzipping file","unzipping the mod to "+self.wd+"/"+name)  
        self.unzip(location,self.wd+"/"+name)
        
        
        self._msg("Cleaning directories","removing unnecessary folders from root")
        roottype = self.folderType(self.wd+"/"+name)
        count = 0
        
        while (roottype == IS_BLANK):
            count = count + 1
            
            if count > 20:
                self.error = 1
                self.errormsg = "Recursive Error"
                return False
                
            subdirs = self.get_immediate_subdirectories(self.wd+"/"+name)
            
            if (len(subdirs)==1):
                os.rename(self.wd+"/"+name, self.wd+"/copy_"+name)
                if not os.path.exists(self.wd+"/"+name):
                    os.makedirs(self.wd+"/"+name)
                my_move(self.wd+"/copy_"+name+"/"+subdirs[0]+"/", self.wd+"/"+name+"/")
            else:
                break
                
            roottype = self.folderType(self.wd+"/"+name)
            shutil.rmtree(self.wd+"/copy_"+name)
        
        self._msg("Cleaning complete","")
        
        if desc!="" and not os.path.isfile(self.wd+"/"+name+"/description.txt"):
            self._msg("Adding description.txt","description.txt was missing from the mod.")
            f = open(self.wd+"/"+name+"/description.txt", "w")
            f.write(desc)
            f.close()
            
        if image!="" and os.path.isfile(image) and not os.path.isfile(self.wd+"/"+name+"/screenshot.png"):
            shutil.copy2(image, self.wd+"/"+name+"/screenshot.png")
            
        safe = self.searchLua(self.wd+"/"+name)
            
        file = self.wd+"/"+name+"_"+str(int(math.floor(random.random()*1000)))+".zip"
        self.zipdir(self.wd+"/"+name,file)
        shutil.rmtree(self.wd+"/"+name)
        return CheckResult(file,safe)
        
    # See what type of file it is
    def folderType(self,path):
        print("Getting folder type of "+path)
        
        if os.path.isfile(path+"/init.lua"):
            print("-- is mod")
            return IS_MOD
        elif os.path.isfile(path+"/modpack.txt"):
            print("-- is modpack")
            return IS_MODPACK
        else:
            print("-- is blank")
            return IS_BLANK
        
        return True
        
    def githubGet(self,github,title,name,desc,image):
        if not os.path.exists(self.wd):
            os.makedirs(self.wd)

        self._msg("Downloading from github","downloading "+github+"/archive/master.zip")
        import urllib2
        u = urllib2.urlopen(github+"/archive/master.zip")
        localFile = open(self.wd+"/github.zip", 'w')
        localFile.write(u.read())
        localFile.close()
        
        return self.run(self.wd+"/github.zip",title,name,desc,image)
        
    def searchLua(self,dir):
        import glob
        files = glob.glob(dir+'/*.lua')
        for f in files:
            rd = open(f).read()
            #if 'os.execute' in rd:
            #    self._msg("Security Risk","os.execute found in "+f,WARNING)  
            #    return "os.execute found in "+f
            #if 'os.io' in rd:
            #    self._msg("Security Risk","os.io found in "+f,WARNING)
            #    return "os.io found in "+f
            def lookfor(sub,reg):
                if sub in rd:
                    import re
                    oses = [m.start() for m in re.finditer(reg, rd)]
                    for o in oses:
                        start = o - 10
                        tend = o + 50
                        
                        if start < 0:
                            start = 0
                        if tend > len(rd):
                           tend = len(rd)
                           
                        b4 = o-1
                        charb4 = -1
                        
                        if (b4>=0):
                            charb4 = rd[b4]
                        
                        if charb4 == "" or charb4=="\n" or charb4 == "\0" or charb4==-1 or charb4=="\t" or charb4==";":
                            self._msg("Possible security risk, needs checking",sub+" used near '"+rd[start:tend].replace("\n"," ")+"'")
            
            lookfor("os.","os\.")
            lookfor("_g","_g")
            lookfor("loadstring","loadstring")
                
        sdirs = [x[0] for x in os.walk(dir)]
        sdirs = sdirs[1:]
        
        for d in sdirs:
            res = self.searchLua(d)
            if res!=0:
                return res
            
        return 0
