# Security Considerations

Standards Lab allows users to upload arbitrary data and schema to the specified file system and run a process on that data.

## Considerations

When thinking about the security implications consider mitigations such as:

- Adding HTTP authentication to restrict to trusted users
- Adding an SSL certificate to the server so that data is transmitted more securely
- Using Standards Lab as a local application that is only available to the localhost
- Isolating any deployment by using containers and virtualisation
- Making sure users understand not to upload any data that may be private
