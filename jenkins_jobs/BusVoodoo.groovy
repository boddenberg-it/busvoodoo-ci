node('BusVoodoo_E2E_CLI') {
timestamps {
    stage('Clean WS'){
        cleanWs()
    }
    stage('Checkout') {
    dir('source') {
	try { // try catch to reuse groovy script for nightly and dev pipeline
		git branch: "${GIT_BRANCH}", url: 'https://git.cuvoodoo.info/stm32f1'
	} catch (MissingPropertyException e) {
		git branch: 'busvoodoo', url: 'https://git.cuvoodoo.info/stm32f1'
	}	 
    }
    sh 'echo "#!/bin/sh" > source/jenkins_build.sh'
    sh 'echo "BUSVOODOO_HARDWARE_VERSION=0 rake; mv application.bin application_v0.bin; rake clean; BUSVOODOO_HARDWARE_VERSION=1 rake; mv application.bin application_vA.bin" >> source/jenkins_build.sh; chmod 755 source/jenkins_build.sh'
    sh 'mkdir xenial bionic stretch archlinux'
    sh 'echo xenial bionic stretch archlinux | xargs -n 1 cp -ar source'
   }

    stage('compile') {
    parallel xenial: {
        sh 'docker run -t --rm=true -v "$(pwd)/xenial/source":/tmp bvbs_xenial ./jenkins_build.sh'
    }, bionic: {
        sh 'docker run -t --rm=true -v "$(pwd)/bionic/source":/tmp bvbs_bionic ./jenkins_build.sh'
    }, stretch: {
        sh 'docker run -t --rm=true -v "$(pwd)/stretch/source":/tmp bvbs_stretch ./jenkins_build.sh'
    }, archlinux: {
        sh 'docker run -t --rm=true -v "$(pwd)/archlinux/source":/tmp bvbs_archlinux ./jenkins_build.sh'
    }
    failFast: false
    }

    stage('archive') {

        sh 'mv xenial/source/application_v0.bin application_v0_xenial.bin || true'
        sh 'mv bionic/source/application_v0.bin application_v0_bionic.bin || true'
        sh 'mv stretch/source/application_v0.bin application_v0_stretch.bin || true'
        sh 'mv archlinux/source/application_v0.bin application_v0_archlinux.bin || true'
        
        sh 'mv xenial/source/application_vA.bin application_vA_xenial.bin || true'
        sh 'mv bionic/source/application_vA.bin application_vA_bionic.bin || true'
        sh 'mv stretch/source/application_vA.bin application_vA_stretch.bin || true'
        sh 'mv archlinux/source/application_vA.bin application_vA_archlinux.bin || true'

        archiveArtifacts '*.bin, *.elf'
    }
    
   //stage('Flash') {
   //	sh 'dfu-util --device "${DEVICE_ID}" --download application_v0_archlinux.bin'
   //}
   
   //stage('Test BusVoodoo v0'){
   //    sh 'BusVoodoo_e2e_tests.py'
   //}
	
   //stage('Expose test report') {
   //    junit healthScaleFactor: 1.5, testResults: '*_test-report.xml'
   //}

}
}
