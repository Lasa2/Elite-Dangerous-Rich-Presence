<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<!-- <br />
<div align="center">
  <a href="https://github.com/Lasa2/Elite-Dangerous-Rich-Presence">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
-->

<h3 align="center">Elite Dangerous Rich Presence</h3>

  <p align="center">
    A standalone Discord Rich Presence application which hides in the System Tray.
    <br />
    <a href="https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/blob/master/README.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/issues">Report Bug</a>
    ·
    <a href="https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
<p align="middle">
  <img src="https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/blob/master/images/presence.jpg?raw=true">
  <img src="https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/blob/master/images/settings.png?raw=true" height=600px>
</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![pypresence][pypresence]][pypresence-url]
* [![flet][flet]][flet-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To simply use the app unpack the latest release and run the Elite Dangerous Rich Presence.exe. To keep your settings between updates simply copy the settings.json file.

If you want to modify and build your own app, then follow the installation and usage guide.

### Prerequisites

* [poetry](https://python-poetry.org/docs/#installation)
  ```powershell
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
  ```

### Installation

1. Clone the repo
   ```powershell
   git clone https://github.com/Lasa2/Elite-Dangerous-Rich-Presence.git
   ```
2. Enter directory
   ```powershell
   Set-Location Elite-Dangerous-Rich-Presence
   ```
3. Install python packages with poetry
   ```powershell
   poetry install
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

<!-- Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources. -->

To run the app without building an executable:
```powershell
poetry run python -m elite_dangerous_rich_presence
```
To build the executable:
```powershell
./build.bat
```

<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

There are currently no features planned, if you have a feature that is missing please [open an issue](https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/issues)

See the [open issues](https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/Lasa2/Elite-Dangerous-Rich-Presence](https://github.com/Lasa2/Elite-Dangerous-Rich-Presence)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Lasa2/Elite-Dangerous-Rich-Presence.svg?style=for-the-badge
[contributors-url]: https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Lasa2/Elite-Dangerous-Rich-Presence.svg?style=for-the-badge
[forks-url]: https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/network/members
[stars-shield]: https://img.shields.io/github/stars/Lasa2/Elite-Dangerous-Rich-Presence.svg?style=for-the-badge
[stars-url]: https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/stargazers
[issues-shield]: https://img.shields.io/github/issues/Lasa2/Elite-Dangerous-Rich-Presence.svg?style=for-the-badge
[issues-url]: https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/issues
[license-shield]: https://img.shields.io/github/license/Lasa2/Elite-Dangerous-Rich-Presence.svg?style=for-the-badge
[license-url]: https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[pypresence]: https://img.shields.io/badge/pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20
[pypresence-url]: https://github.com/qwertyquerty/pypresence
[flet]: https://img.shields.io/badge/flet-db0f49.svg?style=for-the-badge
[flet-url]: https://flet.dev/
