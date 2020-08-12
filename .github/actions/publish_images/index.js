const core = require('@actions/core');
const github = require('@actions/github');
const glob = require('glob');
const path = require('path')
const log = require("npmlog");

const { exec } = require('child_process');
const { spawn } = require('child_process');

try {
  const workspace = process.env.GITHUB_WORKSPACE ? process.env.GITHUB_WORKSPACE + '/**/Dockerfile' : '../../../**/Dockerfile';
  const registryUsername = process.env.REGISTRY_USERNAME ? process.env.REGISTRY_USERNAME : 'mekomsolutions';
  const registryPasswordFile = "secret.txt";
  const registryUrl = process.env.REGISTRY_URL ? process.env.REGISTRY_URL : 'docker.io';

  log.info(registryUsername);
  log.info(registryPasswordFile);
  log.info(registryUrl);

  const gitRef = "latest";
  log.info("Running...")

  // Docker Login
  exec("cat " + registryPasswordFile + " | docker login --username=" +
  registryUsername + " --password-stdin " + registryUrl, (error, stdout, stderr) => {
    if (error) {
      log.error("", `${error}`);
      return;
    }
    log.info("",`${stdout}`);
    log.error("", `${stderr}`);

  // const cat = spawn("cat", [registryPasswordFile])
  // const dockerLogin = spawn("docker", ["login", "--username=" + registryUsername, "--password-stdin", registryUrl])
  // cat.stdout.pipe(dockerLogin.stdin);
  //
  // dockerLogin.stdout.on('data', (data) => {
  //   log.info("", `${data}`);
  // });
  // dockerLogin.stderr.on('data', (data) => {
  //   log.error("", `${data}`);
  //   log.error("", "Unable to log in to Docker registry: \'" + registryUrl + "\'");
  // });
  // dockerLogin.on('close', (code) => {
    log.info("", "Successfully logged in to Docker registry: \'" + registryUrl + "\'");
    // List all Dockerfile files
    glob(workspace, {}, function(er, files) {
      absolute_files = files.map(file => path.resolve(file))

      // Build all Docker images
      absolute_files.forEach(file => {
        var pathAsArray = path.dirname(file).split(path.sep)
        var serviceName = pathAsArray[pathAsArray.length -1]
        var imagePath = registryUsername + "/" + "bahmni:" + serviceName + "-" + gitRef
        const dockerBuildArgs = ["build", "-t", imagePath, path.dirname(file)]
          var dockerBuild = spawn("docker", dockerBuildArgs)
          dockerBuild.stdout.on('data', (data) => {
            log.info("", `${data}`);
          });
          dockerBuild.stderr.on('data', (data) => {
            log.error("", `${data}`);
          });
          dockerBuild.on('close', (code) => {
            log.info("", "Successfully built and tagged " + imagePath + ".");
            // Push the image once built
            log.info("", "Pushing " + imagePath + "...");

            // Push the Docker images
            var dockerPush = spawn("docker", ["push", imagePath]);
            dockerPush.stdout.on('data', (data) => {
              log.info("", `${data}`);
            });
            dockerPush.stderr.on('data', (data) => {
              log.error("", `${data}`);
            });
            dockerPush.on('close', (code) => {
            });
          })
      })
  });
    });
} catch (error) {
  core.setFailed(error.message);
}
