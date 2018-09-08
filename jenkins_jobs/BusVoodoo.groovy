node('BusVoodoo_E2E_CLI') {
timestamps {
    stage('Clean WS + Checkout') {
    cleanWs()
    dir('source') {
	try { // try catch to reuse groovy script for nightly and dev pipeline
		git branch: "${GIT_BRANCH}", url: 'https://git.cuvoodoo.info/stm32f1'
	} catch (MissingPropertyException e) {
		git branch: 'busvoodoo', url: 'https://git.cuvoodoo.info/stm32f1'
	}	 
    }
    // partial https checkout of busvoodoo-ci repo to get latest jenkins_build.sh script 
    sh 'curl -o jenkins_build.sh https://raw.githubusercontent.com/boddenberg-it/busvoodoo-ci/master/jenkins_scripts/jenkins_build.sh; chmod +x jenkins_build.sh; cp jenkins_build.sh source/; ./jenkins_build.sh prepare'
    }

    stage('Compile on distros') {
    parallel xenial: {
        sh 'docker run -t --rm=true -v "$(pwd)/xenial/source":/tmp bvbs_xenial ./jenkins_build.sh xenial'
    }, bionic: {
        sh 'docker run -t --rm=true -v "$(pwd)/bionic/source":/tmp bvbs_bionic ./jenkins_build.sh bionic'
    }, stretch: {
        sh 'docker run -t --rm=true -v "$(pwd)/stretch/source":/tmp bvbs_stretch ./jenkins_build.sh stretch'
    }, archlinux: {
        sh 'docker run -t --rm=true -v "$(pwd)/archlinux/source":/tmp bvbs_archlinux ./jenkins_build.sh archlinux'
    }
    failFast: false
    }

    stage('Archive bins') {
	sh 'cp source/README.md source/LICENSE.txt .'
        archiveArtifacts '*.bin, *.elf, README.md, LICENSE.txt'
    }
    
   // TODO: parallize this step with a BusVoodoo vA slave
   //stage('Flash/boot bionic FW') {
   //	sh 'jenkins_build.sh flash bionic'
   //}

   //stage('Flash/boot xenial FW') {
   //	sh 'jenkins_build.sh flash xenial'
   //}

   //stage('Flash/boot stretch FW') {
   //	sh 'jenkins_build.sh flash archlinux'
   //}

   //stage('Flash/boot arch FW') {
   //	sh 'jenkins_build.sh flash archlinux'
   //}
   //stage('Test BusVoodoo v0'){
   //    sh 'BusVoodoo_e2e_tests.py'
   //}
	
   //stage('Expose test reports') {
   //    junit healthScaleFactor: 1.5, testResults: '*_test-report.xml'
   //}

   //stage('Clean WS') {
   //	cleanWs()
   //}
}
}
