## How to modify BEAST on macOS

Last updated 2025-02-22 by Paul O. Lewis

#### Navigate to the directory in which you want to build beast. For me, this was _~/Documents/software/other/beast_.
 
    cd ~/Documents/software/other
    mkdir beast
    cd beast
 
Note: I think the directory you choose for this should be at least one level above your home directory because (as you will see in the last step), it puts the final product not in the directory you specify above but one level below that.
 
#### Install JDK

(Loosely) following the directions at the bottom of the readme page at https://github.com/CompEvol/BeastFX, I downloaded the DMG for the JDK FX version of azul 23.0.2+7 for maxOS ARM 64-bit (v8) from https://www.azul.com/downloads/?package=jdk to my _~/Documents/software/other/beast_ directory.

---

**Important: be sure to use the "Java Package" dropdown to select "JFK FX".** If you download the plain JFK then you will get errors like the following when trying to compile beast:

    error: package javafx.scene.effect does not exist

Note that the version reported by `java --version` is the same for both JDK and JDK FX, so it is hard to tell whether you have installed the correct version!

---

See instructions at https://docs.azul.com/core/install/macos to install, but, basically, it is as simple as double-clicking the DMG to install. The jdk will be located here: _/Library/Java/JavaVirtualMachines_.

You can check the java version as follows:

    cd /Library/Java/JavaVirtualMachines/zulu-23.jdk/Contents/Home
    ./bin/java --version
    openjdk 23.0.2 2025-01-21
    OpenJDK Runtime Environment Zulu23.32+11-CA (build 23.0.2+7)
    OpenJDK 64-Bit Server VM Zulu23.32+11-CA (build 23.0.2+7, mixed mode, sharing)

Edit *~/.bash_profile* and add the jdk to `PATH` so that it will be available from everywhere:

    export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-23.jdk/Contents/Home
    export PATH=${JAVA_HOME}/bin:${PATH}

#### Download beast2
 
    git clone https://github.com/CompEvol/beast2.git
 
#### Download BeastFX
 
    git clone https://github.com/CompEvol/BeastFX.git
 
#### Modify _BEASTVersion.java_:
 
    bbedit ./beast2/src/beast/pkgmgmt/BEASTVersion.java
 
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

    bbedit ./beast2/src/beast/base/evolution/speciation/SpeciesTreePrior.java
 
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

To create a couple of static global variables in which to keep track of the number of times the likelihood is calculated and the number of partials recalculated, add a directory named _pol_ to _./beast2/src/beast/base_ and navigate into it.

    bbedit ./beast2/src/beast/base/pol/POLGlobals.java

Insert these contents:

    package beast.base.pol; //POL
    
    public class POLGlobals { //POL
    
        static public long likelihoodsCalculated; //POL
        static public long partialsRecalculated; //POL
        
    } 

#### Modify _BeagleTreeLikelihood.java_:

    bbedit ./beast2/src/beast/base/evolution/likelihood/BeagleTreeLikelihood.java

After all the other imports at the top of the file, add

    import beast.base.pol.POLGlobals; //POL

Just after `public double calculateLogP() {`, add this line:

    POLGlobals.likelihoodsCalculated++; //POL

Still inside the `calculateLogP` function, but after the line `traverse(root, null, true);`, add

    POLGlobals.partialsRecalculated += operationCount[0]; //POL

#### Modify _Logger.java_:

    bbedit ./beast/base/inference/Logger.java

After all the other imports at the top of the file, add

    import beast.base.pol.POLGlobals; //POL

In `public void init()` function, change

    for (final Loggable m_logger : loggerList) {
        m_logger.init(out);
    }

    // Remove trailing tab from header
    String header = rawbaos.toString().trim();

to

    for (final Loggable m_logger : loggerList) {
        m_logger.init(out);
    }

    if (mode == LOGMODE.compound && tmp != System.out) {    //POL
        out.print("MPartials\t");                           //POL
    }                                                       //POL

    // Remove trailing tab from header
    String header = rawbaos.toString().trim();

Finally, at the end of the function `public void log(long sampleNr)`, change

        } else {
            m_out.println(logContent);
        }
    } // log

to be 

        } else {
            m_out.print(logContent);                                                //POL
            double num_partial_recalculations = POLGlobals.partialsRecalculated;    //POL
            m_out.print("\t" + (num_partial_recalculations/1000000.0));             //POL
            m_out.println();                                                        //POL
            
            //POL m_out.println(logContent);
        }
    } // log

#### Modify _MCMC.java_:

    bbedit ./beast2/src/beast/base/evolution/inference/MCMC.java

After all the other imports at the top of the file, add

    import beast.base.pol.POLGlobals; //POL

In the function `public void run()`, just after the line `final long startTime = System.currentTimeMillis();`, add

    POLGlobals.partialsRecalculated = 0; //POL added
    POLGlobals.likelihoodsCalculated = 0; //POL added

Just before `close()` near the end of the `run` function, add

    Log.info.println("Total likelihood calculations: " + POLGlobals.likelihoodsCalculated); //POL added
    Log.info.println("Total partials recalculated: " + POLGlobals.partialsRecalculated); //POL added

#### Modify _~/BeastFX/build.xml_

Following the directions at the bottom of the readme page at https://github.com/CompEvol/BeastFX, I modified _build.xml_ in the _BeastFX_ directory, used the XML `<!--` and `-->` code to comment out the old `openjreMac` line and added a version that points to where I installed my zulu-17 java:
 
    bbedit ./BeastFX/build.xml
 
    <!-- POL commented out --> <!--  <property name="openjreMac" value="../../Downloads/zulu17.34.19-ca-fx-jre17.0.3-macosx_x64"/> -->
    <!-- POL added -->
    <property name="openjreMac" value="/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home"/>

#### Build beast2 and BeastFX

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

**Important:** you must delete the _~/Library/Application\ Support/BEAST_ directory before you build. Code in this hidden directory is what is actually executed when you run beast, so failing to remove this directory prior to a build will result in confusion: you will think you have changed beast but much (but not all!) of the code that is run will come from the former version stored in _~/Library/Application\ Support/BEAST_! I have thus added a line in the _buildbeast.sh_ script to always blow away ~/Library/Application\ Support/BEAST_ before starting.

You should create the _buildbeast.sh_ file at the same directory level as your _beast2_ and _BeastFX_ directories.

    cat - > buildbeast.sh
    #!/bin/bash
    
    rm -rf ~/Library/Application\ Support/BEAST
    
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
    ant mac
    cd ..
    <Ctrl-d>

 #### Installing starbeast3 and dependent modules

You should now see the directory _BEAST_ and the file _BEAST v2.7.7.dmg_ in your _beast2/release/Mac/_ directory. 

In order to install starbeast3, you will need to run packagemanager. Unfortunately, packagemanager, as written, blows away the `JAVA_HOME` environmental variable that you set up in *~/.bash_profile* earlier. We can easily fix this, however. Open _beast2/release/Mac/BEAST/BEAST 2.7.7/bin/packagemanager_ using BBEdit,

    bbedit beast2/release/Mac/BEAST/BEAST\ 2.7.7/bin/packagemanager
    
and comment out this line 

    export JAVA_HOME="$BEAST/jre"

making it look like this instead

    #export JAVA_HOME="$BEAST/jre"
    
Now you should be able to run it as follow

    cd beast2/release/Mac/BEAST/BEAST\ 2.7.7/bin
    ./packagemanager -add starbeast3
    
In fact, now that you've commented out the `export JAVA_HOME...` line in _packagemanager_, you can simply add that last command to your _buildbeast.sh_ script so that it looks like this:

    #!/bin/bash
    
    rm -rf ~/Library/Application\ Support/BEAST
    
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
    ant mac
    cd ..
    ./beast2/release/Mac/BEAST/BEAST\ 2.7.7/bin/packagemanager -add starbeast3

#### Running beast

Assuming you have a directory named _~/testbeast_ containing an xml file named _test.xml_, you can run beast now as follows:

    cd ~/testbeast
    BEASTBIN="$HOME/Documents/software/other/beast/beast2/release/Mac/BEAST/BEAST 2.7.7/bin/"
    "$BEASTBIN"/beast -seed 1 -beagle_CPU test.xml

You may wish to create an alias in*~/.bash_profile* to save from having to type the full path to the beast script.

    alias gobeast="~/beast2/release/Mac/BEAT/bin/beast -beagle_CPU"

Alternatively, you can create a _go.sh_ script in your _testbeast_ directory

    cd ~/testbeast
    cat - > go.sh
    #!/bin/bash
    rm -f locus*.trees *.xml.state *.log species.trees
    BEASTBIN="$HOME/Documents/software/other/beast/beast2/release/Mac/BEAST/BEAST 2.7.7/bin/"
    "$BEASTBIN"/beast -seed 1 -beagle_CPU test.xml
    <Ctrl-d>

