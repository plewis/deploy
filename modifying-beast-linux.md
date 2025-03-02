## How to modify BEAST on 64-bit CentOS Linux

Last updated 2025-03-01 by Paul O. Lewis

This installation focusses on installing and modifying beast on the UConn HPC cluster.

Here is the operating system information for the node on which these instructions were tested:

    $ cat /etc/os-release
    NAME="Red Hat Enterprise Linux"
    VERSION="8.10 (Ootpa)"
    ID="rhel"
    ID_LIKE="fedora"
    VERSION_ID="8.10"
    PLATFORM_ID="platform:el8"
    PRETTY_NAME="Red Hat Enterprise Linux 8.10 (Ootpa)"
    ANSI_COLOR="0;31"
    CPE_NAME="cpe:/o:redhat:enterprise_linux:8::baseos"
    HOME_URL="https://www.redhat.com/"
    DOCUMENTATION_URL="https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8"
    BUG_REPORT_URL="https://issues.redhat.com/"
    
    REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 8"
    REDHAT_BUGZILLA_PRODUCT_VERSION=8.10
    REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux"
    REDHAT_SUPPORT_PRODUCT_VERSION="8.10"    

#### Install JDK

(Loosely) following the directions at the bottom of the readme page at https://github.com/CompEvol/BeastFX, I downloaded the _zulu23.32.11-ca-fx-jdk23.0.2-linux_x64.tar.gz_ file from https://www.azul.com/downloads/?package=jdk.

Here is what I chose for each of the four dropdown lists:
* Java Version: Java 23
* Operating System: Linux/CentOS
* Architecture: x86 64-bit
* Java Package: JDK FX

---

**Important: be sure to use the "Java Package" dropdown to select "JFK FX".** If you download the plain JFK then you will get errors like the following when trying to compile beast:

    error: package javafx.scene.effect does not exist

Note that the version reported by `java --version` is the same for both JDK and JDK FX, so it is hard to tell whether you have installed the correct version!

---

See instructions at https://docs.azul.com/core/install/rpm-based-linux to install, but, basically, it is as simple as 

    tar zxvf zulu23.32.11-ca-fx-jdk23.0.2-linux_x64.tar.gz
    
This will create a directory

    zulu23.32.11-ca-fx-jdk23.0.2-linux_x64
    
You can check the java version as follows:

    cd zulu23.32.11-ca-fx-jdk23.0.2-linux_x64
    ./bin/java --version
    openjdk version "23.0.2" 2025-01-21
    OpenJDK Runtime Environment Zulu23.32+11-CA (build 23.0.2+7)
    OpenJDK 64-Bit Server VM Zulu23.32+11-CA (build 23.0.2+7, mixed mode, sharing)

#### Install Apache Ant

Download _apache-ant-1.10.15-bin.tar.gz_ from https://ant.apache.org/bindownload.cgi, copy to HPC cluster, and unpack. This is a java program, so there are no operating-system-specific versions:

    tar zxvf apache-ant-1.10.15-bin.tar.gz

This will create a directory

    apache-ant-1.10.15
    
#### Install BeagleLib

Install BeagleLib according to the instructions at https://github.com/beagle-dev/beagle-lib/wiki/LinuxInstallInstructions. I have modified these instructions below for our particular HPC setup.

First, load some modules

    module load gcc/14.2.0 cmake/3.23.2

Clone the library

    git clone --depth=1 https://github.com/beagle-dev/beagle-lib.git
    
Build the library
    
    cd beagle-lib
    mkdir build
    cd build
    cmake -DCMAKE_INSTALL_PREFIX:PATH=$HOME ..
    make install

#### Update PATH environmental variable so that both java and ant can be found

Edit _~/.bashrc_ and add the _bin_ directories of both ant the jdk to `PATH` so that their applications will be available from everywhere:

    export JAVA_HOME=$HOME/zulu23.32.11-ca-fx-jdk23.0.2-linux_x64
    export PATH=${JAVA_HOME}/bin:$HOME/apache-ant-1.10.15/bin:${PATH}
    
While you are editing _~/.bashrc_, add this line to ensure that the beagle libraries are found when running programs:

    export LD_LIBRARY_PATH=$HOME/lib:$LD_LIBRARY_PATH
    
Once you've finished editing  _~/.bashrc_, source it before continuing

    . ~/.bashrc

#### Clone beast2 into your home directory on the HPC cluster
 
    git clone https://github.com/CompEvol/beast2.git
 
#### Clone BeastFX into your home directory on the HPC cluster
 
    git clone https://github.com/CompEvol/BeastFX.git
 
#### Modify _BEASTVersion.java_:
 
    cd ~/beast2/src/beast/pkgmgmt
    nano BEASTVersion.java
 
In getCredits function, replaced
 
    "Roald Forsberg, Beth Shapiro and Korbinian Strimmer");
 
with
 
    "Roald Forsberg, Beth Shapiro and Korbinian Strimmer",
    "",
    "*** This version modified by Paul O. Lewis ***",
    "*** Uses shape=1000 instead of 2 in gamma  ***",
    "*** distribution of population sizes       ***",
    "*** Search for //POL to find modifications ***"
    }; //POL modified

#### Modify _SpeciesTreePrior.java_:

    cd ~/beast2/src/beast/base/evolution/speciation
    nano SpeciesTreePrior.java
 
In initAndValidate function, replaced

    // bottom prior = Gamma(2,Psi)
    gamma2Prior = new Gamma();
    gamma2Prior.alphaInput.setValue(polshape, gamma2Prior);
    
    gamma2Prior.betaInput.setValue(gammaParameterInput.get(), gamma2Prior);
     
    // top prior = Gamma(4,Psi)
    gamma4Prior = new Gamma();
    final RealParameter parameter = new RealParameter(new Double[]{4.0});
    gamma4Prior.alphaInput.setValue(parameter, gamma4Prior);
            gamma4Prior.betaInput.setValue(gammaParameterInput.get(), gamma4Prior);

with

    // bottom prior = Gamma(2,Psi)
    gamma2Prior = new Gamma();
    final RealParameter polshape = new RealParameter(new Double[]{1000.0}); //POL added
    gamma2Prior.alphaInput.setValue(polshape, gamma2Prior);
    
    gamma2Prior.betaInput.setValue(gammaParameterInput.get(), gamma2Prior);
     
    // top prior = Gamma(4,Psi)
    gamma4Prior = new Gamma();
    //POL deleted: final RealParameter parameter = new RealParameter(new Double[]{4.0});
    final RealParameter parameter = new RealParameter(new Double[]{1000.0}); //POL added
    gamma4Prior.alphaInput.setValue(parameter, gamma4Prior);
    
    gamma4Prior.betaInput.setValue(gammaParameterInput.get(), gamma4Prior);
 
#### Add _POLGlobals.java_:

To create a couple of static global variables in which to keep track of the number of times the likelihood is calculated and the number of partials recalculated, add a directory named _pol_ to _./beast2/src/beast/base_, navigate into it, and create the _POLGlobals.java_ file:

    cd ~/beast2/src/beast/base
    mkdir pol
    cd pol
    cat - > POLGlobals.java
    package beast.base.pol; //POL
    
    public class POLGlobals { //POL
    
        static public long likelihoodsCalculated; //POL
        static public long partialsRecalculated; //POL
        
    } 
    <Ctrl-d>

#### Modify _BeagleTreeLikelihood.java_:

    cd ~/beast2/src/beast/base/evolution/likelihood
    nano BeagleTreeLikelihood.java    

After all the other imports at the top of the file, add

    import beast.base.pol.POLGlobals; //POL

Just after `public double calculateLogP() {`, add this line:

    POLGlobals.likelihoodsCalculated++; //POL

Still inside the `calculateLogP` function, but after the line `traverse(root, null, true);`, add

    POLGlobals.partialsRecalculated += operationCount[0]; //POL

#### Modify _MCMC.java_:

    cd ~/beast2/src/beast/base/evolution/inference
    nano MCMC.java

After all the other imports at the top of the file, add

    import beast.base.pol.POLGlobals; //POL

In the function `public void run()`, just after the line `final long startTime = System.currentTimeMillis();`, add

    POLGlobals.partialsRecalculated = 0; //POL added
    POLGlobals.likelihoodsCalculated = 0; //POL added

Just before `close()` near the end of the `run` function, add

    Log.info.println("Total likelihood calculations: " + POLGlobals.likelihoodsCalculated); //POL added
    Log.info.println("Total partials recalculated: " + POLGlobals.partialsRecalculated); //POL added

#### Modify _~/BeastFX/build.xml_

Following the directions at the bottom of the readme page at https://github.com/CompEvol/BeastFX, I modified _build.xml_ in the _BeastFX_ directory, used the XML `<!--` and `-->` code to comment out the old `openjreLnx` line and added a version that points to where I installed my zulu-23 java:
 
    cd ~/BeastFX
    nano build.xml
 
    <!-- POL commented out --><!--<property name="openjreLnx" value="../../Downloads/zulu17.34.19-ca-fx-jre17.0.3-linux_x64/"/> -->
    <!-- POL added -->            <property name="openjreLnx" value="..//zulu23.32.11-ca-fx-jdk23.0.2-linux_x64"/>
    
Comment out this section of the _BeastFX/build.xml_ file to skip the notarization step. That is, change this

    <antcall target="notarization">
       <param name="dmg.path" value="${dmg.path}"/>
    </antcall> 

to this

    <!-- notarization commented out //POL
    <antcall target="notarization">
      <param name="dmg.path" value="${dmg.path}"/>
    </antcall> 
    -->

If you do not comment out this section, you will eventually be asked to supply your username and password for notarization. I have supplied my apple ID and password for this, which works, but notarization does not seem to be necessary so it saves time to skip it. 
 
During the build, you will see a dialog box pop up that seems to encourage you to drag BEAST to your Applications folder, but just ignore it and it will go away.

#### Create a _buildbeast.sh_ script

I realized that one of the reasons beast was not building was because we changed some of the code, which, understandably, causes some of the unit tests to fail. Hence, I'm using the NoJUnitTest versions of the targets.

**Important:** you must delete the _~/.beast_ directory before you build. Code in this hidden directory is what is actually executed when you run beast, so failing to remove this directory prior to a build will result in confusion: you will think you have changed beast but much (but not all!) of the code that is run will come from the former version stored in _~/.beast_! I have thus added a line in the _buildbeast.sh_ script to always blow away _~/.beast_ before starting.

    cd ~
    cat - > buildbeast.sh
    #!/bin/bash
    
    rm -rf ~/.beast
    
    cd beast2
    ant clean
    ant
    cd ../BeastFX
    ant cleanBeastFX
    ant build_jar_all_BEAST_NoJUnitTest
    ant build_jar_all_BeastFX_NoJUnitTest
    ant dist_all_BEAST
    ant dist_all_BeastFX
    ant package
    ant linux
    cd ..
    <Ctrl-d>
    
#### Installing starbeast3 and dependent modules

You should now find the file _BEAST.v2.7.7.tgz_ in _~/beast2/release/Linux_. 

In order to install starbeast3, you will need to run the packagemanager app. Unfortunately, the packagemanager app, as written, blows away the `JAVA_HOME` environmental variable that you set up in _~/.bashrc_ earlier. We can easily fix this, however. Open _~/beast2/release/Linux/beast/bin/packagemanager_ using nano,

    nano ~/beast2/release/Linux/beast/bin/packagemanager
    
and comment out this line 

    export JAVA_HOME="$BEAST/jre"

making it look like this instead

    #export JAVA_HOME="$BEAST/jre"
    
Now you should be able to run it as follow

    cd ~/beast2/release/Linux/beast/bin
    ./packagemanager -add starbeast3
    
In fact, now that you've commented out the `export JAVA_HOME...` line in _packagemanager_, you can simply add that last command to your _buildbeast.sh_ script so that it looks like this:

    #!/bin/bash
    
    rm -rf ~/.beast
    
    cd beast2
    ant clean
    ant
    cd ../BeastFX
    ant cleanBeastFX
    ant build_jar_all_BEAST_NoJUnitTest
    ant build_jar_all_BeastFX_NoJUnitTest
    ant dist_all_BEAST
    ant dist_all_BeastFX
    ant package
    ant linux
    cd ../beast2/release/Linux/beast/bin/packagemanager -add starbeast3

#### Running beast

Assuming you have a directory named _~/testbeast_ containing an xml file named _test.xml_, you can run beast now as follows:

    cd ~/testbeast
    ~/beast2/release/Linux/beast/bin/beast -beagle_CPU test.xml

You may wish to create an alias in _~/.bashrc_ to save from having to type the full path to the beast script.

    alias gobeast="~/beast2/release/Linux/beast/bin/beast -beagle_CPU"

Alternatively, you can create a _go.sh_ script in your _testbeast_ directory

    cd ~/testbeast
    cat - > go.sh
    #!/bin/bash
    rm -f locus*.trees *.xml.state *.log species.trees
    ~/beast2/release/Linux/beast/bin/beast -beagle_CPU tmp.xml
    <Ctrl-d>


