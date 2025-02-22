## How to modify BEAST on macOS

Last updated 2025-02-22 by Paul O. Lewis

#### Important

* These instructions are for macOS and will need some modification for other operating systems

* In order to modify BEAST and actually use your modifications, it is critical that you blow away the folder _~/Library/Application Support/BEAST_. If you don't, then class files in that directory will be preferred over the ones you've modified!

#### Navigate to the directory in which you want to build beast
 
`cd ~/Documents/software/other`
 
Note: I think the directory you choose for this should be at least one level above your home directory because (as you will see in the last step), it puts the final product not in the directory you specify above but one level below that.
 
#### Create beast directory

Created a directory named _beast_ in _~/Documents/software/other_ and then navigated into it:

`cd ~/Documents/software/other/beast`

#### Install JDK

(Loosely) following the directions at the bottom of the readme page at https://github.com/CompEvol/BeastFX, I downloaded the DMG for the JDK FX version of azul 23.0.2+7 for maxOS ARM 64-bit (v8) from https://www.azul.com/downloads/?package=jdk to my _~/Documents/software/other/beast_ directory.

---

**Important: be sure to use the "Java Package" dropdown to select "JFK FX".** If you download the plain JFK then you will get errors like the following when trying to compile beast:

`error: package javafx.scene.effect does not exist`

Note that the version reported by `java --version` is the same for both JDK and JDK FX, so it is hard to tell whether you have installed the correct version!

---

See instructions at https://docs.azul.com/core/install/macos to install, but, basically, it is as simple as double-clicking the DMG to install. The jdk will be located here: _/Library/Java/JavaVirtualMachines_.

You can check the java version as follows:

```
cd /Library/Java/JavaVirtualMachines/zulu-23.jdk/Contents/Home
./bin/java --version
openjdk 23.0.2 2025-01-21
OpenJDK Runtime Environment Zulu23.32+11-CA (build 23.0.2+7)
OpenJDK 64-Bit Server VM Zulu23.32+11-CA (build 23.0.2+7, mixed mode, sharing)
```

Edit _~/.bash_profile_ and add the jdk to `PATH` so that it will be available from everywhere:

```
export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-23.jdk/Contents/Home
export PATH=${JAVA_HOME}/bin:${PATH}
```

#### Download beast2
 
`git clone https://github.com/CompEvol/beast2.git`
 
#### Download BeastFX
 
`git clone https://github.com/CompEvol/BeastFX.git`
 
#### Modify _BEASTVersion.java_:
 
`bbedit ./beast2/src/beast/pkgmgmt/BEASTVersion.java`
 
In getCredits function, replaced
 
`"Roald Forsberg, Beth Shapiro and Korbinian Strimmer");`
 
with
 
```
"Roald Forsberg, Beth Shapiro and Korbinian Strimmer",
"",
"*** This version modified by Paul O. Lewis ***",
"*** Uses shape=1000 instead of 2 in gamma  ***",
"*** distribution of population sizes       ***",
"*** Search for //POL to find modifications ***"
}; //POL modified
```

 #### Modify _SpeciesTreePrior.java_:

`bbedit ./beast2/src/beast/base/evolution/speciation/SpeciesTreePrior.java`
 
In initAndValidate function, replaced
``` 
// bottom prior = Gamma(2,Psi)
gamma2Prior = new Gamma();
gamma2Prior.alphaInput.setValue(polshape, gamma2Prior);

gamma2Prior.betaInput.setValue(gammaParameterInput.get(), gamma2Prior);
 
// top prior = Gamma(4,Psi)
gamma4Prior = new Gamma();
final RealParameter parameter = new RealParameter(new Double[]{4.0});
gamma4Prior.alphaInput.setValue(parameter, gamma4Prior);
        gamma4Prior.betaInput.setValue(gammaParameterInput.get(), gamma4Prior);
``` 
with
``` 
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
```
 
#### Add _POLGlobals.java_:

To create a couple of static global variables in which to keep track of the number of times the likelihood is calculated and the number of partials recalculated, add a directory named _pol_ to _./beast2/src/beast/base_ and navigate into it.

`bbedit ./beast2/src/beast/base/pol/POLGlobals.java`

Insert these contents:

```
package beast.base.pol; //POL

public class POLGlobals { //POL

	static public long likelihoodsCalculated; //POL
	static public long partialsRecalculated; //POL
	
} 
```

#### Modify _BeagleTreeLikelihood.java_:

`bbedit ./beast2/src/beast/base/evolution/likelihood/BeagleTreeLikelihood.java`

After all the other imports at the top of the file, add

```
import beast.base.pol.POLGlobals; //POL
```

Just after `public double calculateLogP() {`, add this line:

```
POLGlobals.likelihoodsCalculated++; //POL
```

Still inside the `calculateLogP` function, but after the line `traverse(root, null, true);`, add

```
POLGlobals.partialsRecalculated += operationCount[0]; //POL
```

#### Modify _MCMC.java_:

`bbedit ./beast2/src/beast/base/evolution/inference/MCMC.java`

After all the other imports at the top of the file, add

```
import beast.base.pol.POLGlobals; //POL
```

In the function `public void run()`, just after the line `final long startTime = System.currentTimeMillis();`, add

```
POLGlobals.partialsRecalculated = 0; //POL added
POLGlobals.likelihoodsCalculated = 0; //POL added
```

Just before `close()` near the end of the `run` function, add

```
Log.info.println("Total likelihood calculations: " + POLGlobals.likelihoodsCalculated); //POL added
Log.info.println("Total partials recalculated: " + POLGlobals.partialsRecalculated); //POL added
```

#### Modify build.xml

Following the directions at the bottom of the readme page at https://github.com/CompEvol/BeastFX, I modified _build.xml_ in the _BeastFX_ directory, used the XML `<!--` and `-->` code to comment out the old `openjreMac` line and added a version that points to where I installed my zulu-17 java:
 
`bbedit ./BeastFX/build.xml`
 
```
<!-- POL commented out --> <!--  <property name="openjreMac" value="../../Downloads/zulu17.34.19-ca-fx-jre17.0.3-macosx_x64"/> -->
<!-- POL added -->
<property name="openjreMac" value="/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home"/>
 ```
#### Build the default beast2 target

```
cd beast2
ant
```
#### Build beast2 and BeastFX

Comment out this section of the _BeastFX/build.xml_ file to skip the notarization step. That is, change this

```
<antcall target="notarization">
   <param name="dmg.path" value="${dmg.path}"/>
</antcall> 
```

to this

```
<!-- notarization commented out //POL
<antcall target="notarization">
  <param name="dmg.path" value="${dmg.path}"/>
</antcall> 
-->
```

If you do not comment out this section, you will eventually be asked to supply your username and password for notarization. I have supplied my apple ID and password for this, which works, but notarization does not seem to be necessary so it saves time to skip it. 
 
I realized that one of the reasons beast was not building was because we changed some of the code, which, understandably, causes some of the unit tests to fail. Hence, I'm using the NoJUnitTest versions of the targets.

During the build, you will see a dialog box pop up that seems to encourage you to drag BEAST to your Applications folder, but just ignore it and it will go away.

```
cd ../BeastFX
ant build_jar_all_BEAST_NoJUnitTest
ant build_jar_all_BeastFX_NoJUnitTest
ant dist_all_BEAST
ant dist_all_BeastFX
ant package
ant mac
```
 
#### DMG

You should now find the beast DMG in _../../tmp_. In my case, it is here:
 
```
~/Documents/software/tmp
```

Note, however, that you **do not need to install the DMG to use beast**. Here is a shell script I use to run beast:

```
#!/bin/bash

rm -rf ~/Library/Application\ Support/BEAST
rm -f test-green7.trees
rm -f test.log
rm -f test.xml.state
~/Documents/software/other/beast/beast2/release/Mac/BEAST/BEAST\ 2.7.7/bin/beast test.xml
```
