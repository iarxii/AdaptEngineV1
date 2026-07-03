<!doctype html>
<html>

<head>
  <meta charset="utf-8">
  <!-- Enable users to add your web application or webpage link to the Home screen. Replace icon.png with your icon file path -->
  <link rel="apple-touch-icon" href="icon.png">
  <!-- Specify a launch screen image that is displayed while your web application launches. Replace app.png with your image file path -->
  <link rel="apple-touch-startup-image" href="app.png">
  <!-- Mobile Internet Explorer allows us to activate ClearType technology for smoothing fonts for easy reading -->
  <meta http-equiv="cleartype" content="on">
  <!-- Specify whether or not telephone numbers in the HTML content should appear as hypertext links -->
  <meta name="format-detection" content="telephone=no" />
  <!-- Changes the logical window size used when displaying a page mobile browsers -->
  <meta name="viewport" content="width = device-width, initial-scale=1, user-scalable=yes">

  <!-- Provide a short description of the page. -->
  <meta name="description" content="AdaptEngine is a Curated Research and Knowledgebase Search Index. The core purpose of theis Search Engine is to index Research Web Resources based on the Content Creation Policy of AdaptivConcept's IT Solutions, Rsearch, Media Content and Platforms developed by AdaptivConcept. Visit https://www.adaptivconcept.co.za for more.">
  <!-- This meta tag tells Google not to show the sitelinks search box. -->
  <meta name="google" content="nositelinkssearchbox" />
  <!-- Control the behavior of search engine crawling and indexing. 
     The robots meta tag applies to all search engines, while the "googlebot" meta tag is specific to Google. -->
  <meta name="robots" content="..., ..." />
  <meta name="http-equiv" content="X-Robots-Tag : noindex, follow" />
  <meta name="googlebot" content="..., ..." />
  <!-- Used for verifying ownership of a site. -->
  <meta name="verify" content="" />

  <!-- Open Graph Meta Tags -->
  <!-- Set the canonical URL for the page you are sharing. -->
  <meta property="og:url" content="http://www.mySite.com/">
  <!-- The title to accompany the URL. -->
  <meta property="og:title" content="AdaptivEngine by AdaptivConcept" />
  <!-- Provides Facebook the name that you would like your website to be recognized by. -->
  <meta property="og:site_name" content="AdaptEngine_ZA">
  <!-- Provides Facebook the type of website that you would like your website to be categorized by. -->
  <meta property="og:type" content="Research">
  <!-- Defines the language, American English is the default. -->
  <meta property="og:locale" content="en-IN">
  <!-- Directs Facebook to use the specified image when the page is shared. -->
  <meta property="og:image" content="image URL">
  <!-- Similar to the meta description tag in HTML. This description is shown below the link title on Facebook. -->
  <meta property="og:description" content="AdaptEngine is a Curated Research and Knowledgebase Search Index. The core purpose of theis Search Engine is to index Research Web Resources based on the Content Creation Policy of AdaptivConcept's IT Solutions, Rsearch, Media Content and Platforms developed by AdaptivConcept. Visit https://www.adaptivconcept.co.za for more." />

  <!-- Twitter Card data -->
  <!-- The type of card to be created: summary, photo, or video -->
  <meta name="twitter:card" content="summary" />
  <!-- Title of the Twitter Card -->
  <meta name="twitter:title" content="AdaptEngine is a Curated Research and Knowledgebase Search Index." />
  <!-- Description of content -->
  <meta name="twitter:description" content="AdaptEngine is a Curated Research and Knowledgebase Search Index. The core purpose of theis Search Engine is to index Research Web Resources based on the Content Creation Policy of AdaptivConcept's IT Solutions, Rsearch, Media Content and Platforms developed by AdaptivConcept. Visit https://www.adaptivconcept.co.za for more." />
  <!-- URL of image to use in the card. Used with summary, summary_large_image, player cards -->
  <meta name="twitter:image" content="" />

  <title>AdaptEngine.v1 | &copy; 2021 AdaptivConcept</title>

  <!-- Font Awesome -->
  <script src="https://kit.fontawesome.com/a2763a58b1.js"></script>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>

<body>
  <!-- The fixed navbar will overlay your other content, unless you add padding to the bottom of the <body>. Tip: By default, the navbar is 50px high.  -->
  <nav class="navbar navbar-expand-lg fixed-top navbar-dark bg-dark p-4 shadow">
    <a class="navbar-brand" href="#">AdaptEngine&trade;_ZA | Curated Research Engine</a>
    <!--<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
       <span class="navbar-toggler-icon"></span>
       </button>-->
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav nav mr-auto justify-content-end">
        <li class="nav-item active">
          <a class="nav-link" href="#">Sign In <span class="sr-only">(current)</span></a>
        </li>
      </ul>
    </div>
  </nav>

  <!---->
  <nav class="navbar navbar-expand-lg fixed-bottom bg-transparent p-4 shadow text-right">
    <p><?php echo "Crafted by AdaptivConcept &copy; " . date('Y'); ?></p>
  </nav>

  <div class="container h-100" style="padding-top: 150px; padding-bottom: 150px;">
    <h1 class="text-center"><span id="greeting"></span>. Welcome to AdaptEngine | V1</h1>
    <p class="text-center">How can we assist you today?</p>

    <div>
      <div class="form-group row py-2">
        <label for="search-term-input" class="col-md-4 col-form-label"><i class="fas fa-search"></i> Search for:</label>
        <div class="col-md-8">
          <input type="text" class="form-control form-control-lg rounded-pill shadow" id="search-term-input" placeholder="Search for a term/keyword/topic">
        </div>
      </div>

      <div class="form-group row py-2">
        <label for="topic-select-input" class="col-md-4 col-form-label"><i class="fas fa-bullhorn"></i> Or Select a Topic</label>
        <div class="col-md-8">
          <!--<input type="password" class="form-control" id="inputPassword3" placeholder="Password">-->
          <select class="form-control form-control-lg rounded-pill shadow" id="topic-select-input" placeholder="Research Topics">
            <option value="no_selection" selected>Select a Topic</option>

            <option value='Aerospace'>Aerospace</option>
            <option value='Agriculture'>Agriculture</option>
            <option value='Algebra'>Algebra</option>
            <option value='Animals'>Animals</option>
            <option value='Archaeology'>Archaeology</option>
            <option value='Architecture'>Architecture</option>
            <option value='Arithmetic'>Arithmetic</option>
            <option value='Artificial intelligence'>Artificial intelligence</option>
            <option value='Astronomy'>Astronomy</option>
            <option value='Big Science'>Big Science</option>
            <option value='Biochemistry'>Biochemistry</option>
            <option value='Biology'>Biology</option>
            <option value='Biotechnology'>Biotechnology</option>
            <option value='Botany'>Botany</option>
            <option value='Business'>Business</option>
            <option value='Calculus'>Calculus</option>
            <option value='Chemistry'>Chemistry</option>
            <option value='Classical antiquity'>Classical antiquity</option>
            <option value='Classical studies'>Classical studies</option>
            <option value='Communication'>Communication</option>
            <option value='Community'>Community</option>
            <option value='Computer science'>Computer science</option>
            <option value='Cooking'>Cooking</option>
            <option value='Crafts'>Crafts</option>
            <option value='Criminal justice'>Criminal justice</option>
            <option value='Critical theory'>Critical theory</option>
            <option value='Culture'>Culture</option>
            <option value='Dance'>Dance</option>
            <option value='Discrete mathematics'>Discrete mathematics</option>
            <option value='Drawing'>Drawing</option>
            <option value='Earth sciences'>Earth sciences</option>
            <option value='Ecology'>Ecology</option>
            <option value='Economics'>Economics</option>
            <option value='Education'>Education</option>
            <option value='Energy development'>Energy development</option>
            <option value='Engineering'>Engineering</option>
            <option value='Exercise'>Exercise</option>
            <option value='Fiction'>Fiction</option>
            <option value='Film'>Film</option>
            <option value='Finance'>Finance</option>
            <option value='Firefighting'>Firefighting</option>
            <option value='Game'>Game</option>
            <option value='Geography'>Geography</option>
            <option value='Geometry'>Geometry</option>
            <option value='Health'>Health</option>
            <option value='Health science'>Health science</option>
            <option value='History'>History</option>
            <option value='Hobbies'>Hobbies</option>
            <option value='Humanism'>Humanism</option>
            <option value='Industry'>Industry</option>
            <option value='Information technology'>Information technology</option>
            <option value='Internet'>Internet</option>
            <option value='Law'>Law</option>
            <option value='Library and information science'>Library and information science</option>
            <option value='Linguistics'>Linguistics</option>
            <option value='Literature'>Literature</option>
            <option value='Logic'>Logic</option>
            <option value='Machines'>Machines</option>
            <option value='Management'>Management</option>
            <option value='Manufacturing'>Manufacturing</option>
            <option value='Marketing'>Marketing</option>
            <option value='Mathematics'>Mathematics</option>
            <option value='Medieval history (Middle Ages)'>Medieval history (Middle Ages)</option>
            <option value='Military'>Military</option>
            <option value='Music'>Music</option>
            <option value='Nutrition'>Nutrition</option>
            <option value='Opera'>Opera</option>
            <option value='Painting'>Painting</option>
            <option value='Performing arts'>Performing arts</option>
            <option value='Permaculture'>Permaculture</option>
            <option value='Philosophical theories'>Philosophical theories</option>
            <option value='Philosophy'>Philosophy</option>
            <option value='Photography'>Photography</option>
            <option value='Physics Fractions'>Physics Fractions</option>
            <option value='Poetry'>Poetry</option>
            <option value='Political science'>Political science</option>
            <option value='Politics'>Politics</option>
            <option value='Programming'>Programming</option>
            <option value='Psychology'>Psychology</option>
            <option value='Public affairs'>Public affairs</option>
            <option value='Relationships'>Relationships</option>
            <option value='Religion'>Religion</option>
            <option value='Renaissance'>Renaissance</option>
            <option value='Robotics'>Robotics</option>
            <option value='Sculpture'>Sculpture</option>
            <option value='Social sciences'>Social sciences</option>
            <option value='Society'>Society</option>
            <option value='Sociology'>Sociology</option>
            <option value='Software engineering'>Software engineering</option>
            <option value='Space exploration'>Space exploration</option>
            <option value='Sports'>Sports</option>
            <option value='Statistics'>Statistics</option>
            <option value='Telecommunication (Internet)'>Telecommunication (Internet)</option>
            <option value='Theatre'>Theatre</option>
            <option value='Thinking'>Thinking</option>
            <option value='Transhumanism'>Transhumanism</option>
            <option value='Transport'>Transport</option>
            <option value='Trigonometry'>Trigonometry</option>
            <option value='Typography'>Typography</option>
            <option value='Vehicles'>Vehicles</option>
            <option value='Visual arts'>Visual arts</option>
            <option value='Zoology'>Zoology</option>

          </select>
        </div>
      </div>

      <div class="form-group row py-2">
        <label for="url-crawl-input" class="col-md-4 col-form-label"><i class="fas fa-link"></i> Or Search from a Web-Link (URL): </label>
        <div class="col-md-8">
          <input type="text" class="form-control form-control-lg rounded-pill shadow" id="url-crawl-input" placeholder="Provide a starting point website link.">
        </div>
      </div>

      <div class="form-group row pt-2">
        <div class="col-12 text-end">
          <button onclick="executeSearch()" class="btn btn-dark btn-lg rounded-pill shadow-lg">Search <i class="fas fa-arrow-alt-circle-right"></i></button>
        </div>
      </div>
  </div>

    <img src="" alt="" class="img-fluid">
  </div>

  <script>
    function getTime() {
      var dd = new Date();
      var hh = dd.getHours();

      if (hh > 11) {
        document.getElementById('greeting').innerText = "Good afternoon";
      } else {
        document.getElementById('greeting').innerText = "Good morning";
      }

    }

    getTime();

    function executeSearch() {
      var inputSearchTerm = document.getElementById('search-term-input');
      var inputSearchTopic = document.getElementById('topic-select-input');
      var inputCrawlUrl = document.getElementById('url-crawl-input');

      // encodeURI(inputCrawlUrl);

      if (inputSearchTerm.value.length !== 0) window.open("search/?process=search_term&q=" + encodeURI(inputSearchTerm.value), '_blank');

      if (inputSearchTopic.value !== "no_selection") window.open("search/?process=search_topic&q=" + encodeURI(inputSearchTopic.value), '_blank');

      if (inputCrawlUrl.value.length !== 0) window.open("search/?process=url_crawl&q=" + encodeURI(inputSearchTerm.value), '_blank');
    }
  </script>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>

</body>

</html>