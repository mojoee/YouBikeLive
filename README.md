<!-- Improved compatibility of back to top link: See: https://github.com/mojoee/YouBikeLive/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



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
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/mojoee/YouBikeLive">
    <img src="docs/TaiwanFlag.svg" alt="Logo" width="90" height="60">
  </a>

  <h3 align="center">YouBikeLive</h3>

  <p align="center">
    An awesome Visualization of YouBike2.0 Stations in Taipei City!
    <br />
    <a href="https://github.com/mojoee/YouBikeLive"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/mojoee/YouBikeLive">View Demo</a>
    ·
    <a href="https://github.com/mojoee/YouBikeLive/issues">Report Bug</a>
    ·
    <a href="https://github.com/mojoee/YouBikeLive/issues">Request Feature</a>
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

[![Product Name Screen Shot][product-screenshot]](https://example.com)

This project uses the open source data available from Taipei about the YouBike2.0 stations in the city. It displays the data in an interactive web app.

What is displayed:
* available bikes and available slots at each of the 1299 stations in Taipei City. 
* the size (number of total bike slots) of the stations displayed as the radius of the station
* the usage of the station (ratio of size and available bikes)

This repo also explores the YouBike Rental Trip data from 2023, which can be found [here](https://data.gov.tw/en/datasets/169174).


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [![bokeh][bokeh.js]][bokeh-url]
* [![poetry][poetry.py]][poetry-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

You can easily download the project and host it locally.

### Prerequisites

If you want to host it locally, you need the following:
* google API key

### Installation

The project is managed with poetry and will make it easy to use on your machine.

1. poetry install


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

You can reach the web-hosted page [here](https://youbikelive-1997a5b6ef93.herokuapp.com/myapp).



<!-- ROADMAP -->
## Roadmap

- [x] Add local deployment
- [x] Add back to top links
- [ ] Add heroku deployment
- [x] Draw database management 
- [x] Populate the two new tables with all the data
- [ ] Figure out a way to calculate the demand
- [x] Add scraping for the weather DB
- [ ] checkout Nikos API

See the [open issues](https://github.com/mojoee/YouBikeLive/issues) for a full list of proposed features (and known issues).

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

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Moritz Sontheimer - moritzsontheimer@web.de

Project Link: [https://github.com/mojoee/YouBikeLive](https://github.com/mojoee/YouBikeLive)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Tutorial on data visualization](https://thedatafrog.com/en/articles/show-data-google-map-python/)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [README layout](https://github.com/mojoee/YouBikeLive)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [Taipei Open Source Data](https://data.taipei/dataset?qs=youbike)
* [OSRM Tutorial](https://www.afi.io/blog/introduction-to-osrm-setting-up-osrm-backend-using-docker/?ref=blog.afi.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/mojoee/YouBikeLive.svg?style=for-the-badge
[contributors-url]: https://github.com/mojoee/YouBikeLive/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/mojoee/YouBikeLive.svg?style=for-the-badge
[forks-url]: https://github.com/mojoee/YouBikeLive/network/members
[stars-shield]: https://img.shields.io/github/stars/mojoee/YouBikeLive.svg?style=for-the-badge
[stars-url]: https://github.com/mojoee/YouBikeLive/stargazers
[issues-shield]: https://img.shields.io/github/issues/mojoee/YouBikeLive.svg?style=for-the-badge
[issues-url]: https://github.com/mojoee/YouBikeLive/issues
[license-shield]: https://img.shields.io/github/license/mojoee/YouBikeLive.svg?style=for-the-badge
[license-url]: https://github.com/mojoee/YouBikeLive/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/moritz-sontheimer-23bb40156/
[product-screenshot]: docs/AppGUI.png
[bokeh-url]: http://bokeh.org/
[Bokeh.js]: https://img.shields.io/badge/Bokeh-20232A?style=for-the-badge&logo=bokeh&logoColor=61DAFB
[poetry-url]: https://python-poetry.org/
[poetry.py]: https://img.shields.io/badge/Poetry-7cfc00?style=for-the-badge&logo=poetry&logoColor=blue
