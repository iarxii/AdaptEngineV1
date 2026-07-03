<?php

include( "../scripts/php/config.php" );

//Connection Test - Check connection ==============================================> 
if ($db->connect_error) {
    die("<div class='p-4 alert alert-danger'>Connection failed: " . $db->connect_error) . "</div>";
}
echo "Connected successfully \n\n";
//end of Connection Test============================================>

// declaring variables
$startURL = "";
$already_crawled = array();
$crawling = array();

// check if query web url has been passed in get parameters, if not then get the last url from db and continue crawling from there
if (isset($_GET[ 'startURL' ])) {
    $startURL = $_GET[ 'startURL' ];
    
    if (filter_var($startURL, FILTER_VALIDATE_URL) === FALSE) {
        //Not a valid URL - get the last crawled url from db
        $start = get_last_crawl_url(); 
    } else {
        $start = $startURL;
    }
} else {
    //go to home page
    header("Location: ../");
}

function get_last_crawl_url() {
    global $db;
    $last_crawled_url = $last_crawled_urlhash = "";

    try {
        $query = "SELECT `url`, `url_hash` FROM `index` ORDER BY id DESC LIMIT 1";

        $result = $db->query($query);

        if (!$result) die("A Fatal Error has occured. Please reload the page, and if the problem persists, please contact the system administrator.");

        $rows = $result->num_rows;

        for ($j = 0; $j < $rows; ++$j) {
            $row = $result->fetch_array(MYSQLI_ASSOC);

            $last_crawled_url = htmlspecialchars($row['url']);
            // $last_crawled_urlhash = htmlspecialchars($row['url_hash']);
        }

        return $last_crawled_url;
    } catch (\Throwable $th) {
        //throw $th;
        die("An Exception error occurred while attempting to get last crawled URL: [ $th ]");
    }
}

function get_favicon ($url) {

	$save_file_path = '../media/crawler/favicons/';

    $domain = parse_url($url)['host'];
    $filepath = $save_file_path . $domain . ".ico";

    if (!file_exists ($filepath)) {
        
        file_put_contents ($filepath, file_get_contents ('https://www.google.com/s2/favicons?domain=' . $domain));
    }

    return $filepath;
}

function clean($string) {
   //$string = str_replace(' ', '-', $string); // Replaces all spaces with hyphens.
   $string = preg_replace('/[^A-Za-z0-9\-]/', ' ', $string); // Removes special chars.

   return preg_replace('/-+/', '-', $string); // Replaces multiple hyphens with single one.
}

function cleanKeywords($string) {
    $string = preg_replace('/[^A-Za-z0-9\-]/', '_', $string); // Removes special chars and leave space.
    //$string = str_replace(' ', ',', $string); // Replaces all spaces with commas.

    return preg_replace('/-+/', '-', $string); // Replaces multiple hyphens with single one.
}

function get_details($url) {
    $options = array('http'=>array('method'=>'GET', 'headers'=>"User-Agent: AdaptEngine.v1\n"));
    
    $context = stream_context_create($options);
    
    $doc = new DOMDocument();
    @$doc->loadHTML(@file_get_contents($url, false, $context));
    
    $title = $doc->getElementsByTagName("title");
    @$title = $title->item(0)->nodeValue;
    
    //echo $title."\n";
    $description = $type = $keywords = $image_url = $favicon = $page_content = "";
    $metas = $doc->getElementsByTagName("meta");

    for ($i = 0; $i < $metas->length; $i++) {
        $meta = $metas->item($i);
        
        if ($meta->getAttribute("name") == strtolower("description")) {
            $description = $meta->getAttribute("content");
        }

        if ($meta->getAttribute("name") == strtolower("type")) {
            $type = $meta->getAttribute("content");
        }
        
        if ($meta->getAttribute("name") == strtolower("keywords")) {
            $keywords = $meta->getAttribute("content");
        }

        if ($meta->getAttribute("name") == strtolower("image")) {
            $image_url = $meta->getAttribute("content");
        }
    }

    // $page_contents =  $doc->getElementsByTagName("body"); // "page content here";

    // for ($i = 0; $i < $page_contents->length; $i++) {
    //     $page_content = $page_contents->item($i);

    //     $page_body = $doc->savehtml($page_content)
    // }

    $body = $doc->getElementsByTagName('body');
    
    if ( $body && 0 < $body->length ) {
        $body = $body->item(0);
        $page_content = $doc->savehtml($body);
    }

    $favicon = get_favicon($url);
    
    //added by me: if title, desciption and keywords are empty, then do not return anythin/skip output
    if (is_null($title) || is_null($description) || is_null($keywords)  || is_null($url)) {

     } else {
        return '{ "Title": "'.str_replace("\n", "", $title).'", "Description": "'.str_replace("\n", "", $description).'", "Type": "'.str_replace("\n", "", $type).'", "Keywords": "'.$keywords.'", "URL": "'.$url.'", "Image": "'.str_replace("\n", "", $image_url).'", "Favicon": "'.str_replace("\n", "", $favicon).'", "Content": "'.$page_content.'" }';
    }
    
}

function follow_links($url) {
    
    global $db;
    global $already_crawled;
    global $crawling;
    global $pdo;
    
    $options = array('http'=>array('method'=>'GET', 'headers'=>"User-Agent: AdaptEngine.v1\n"));
    
    $context = stream_context_create($options);
    
    $doc = new DOMDocument();
    @$doc->loadHTML(@file_get_contents($url, false, $context));
    
    $linklist = $doc->getElementsByTagName("a");
    
    foreach ($linklist as $link) {
        $l = $link->getAttribute("href");
        
        //handling URL's that start with '/' or "one forward slash"-which signifies that the link is relative to the host
        if (substr($l, 0, 1) == "/" && substr($l, 0, 2) != "//") {
            $l = parse_url($url)["scheme"]."://".parse_url($url)["host"].$l;
        } 
        //handling URL's that start with '//' or "double slash"-which is missing just the scheme type (http or https)
        else if (substr($l, 0, 2) == "//") {
            $l = parse_url($url)["scheme"].":".$l;
        } 
        //handling URL's that start with './' or "dot-slash"-which is missing the scheme, host name, and path to the resource following the './'
        else if (substr($l, 0, 2) == "./") {
            $l = parse_url($url)["scheme"]."://".parse_url($url)["host"].dirname(parse_url($url)["path"]).substr($l, 1);
        } 
        //handling URL's that start with '#' or "hash-tag"-which are locations/places on the page that is being parsed.
        else if (substr($l, 0, 1) == "#") {
            $l = parse_url($url)["scheme"]."://".parse_url($url)["host"].parse_url($url)["path"].$l;
        } 
        //handling URL's that start with '../' or "dot-dot-slash"-which are links relative to the page that is being parsed but are missing the scheme and host name
        else if (substr($l, 0, 3) == "../") {
            $l = parse_url($url)["scheme"]."://".parse_url($url)["host"]."/".$l;
        } 
        //ignore javascript: links
        else if (substr($l, 0, 11) == "javascript:") {
            continue;
        }
        //handling URL's that do not start with 'https'/'http'
        else if (substr($l, 0, 5) != "https" & substr($l, 0, 4) != "http") {
            $l = parse_url($url)["scheme"]."://".parse_url($url)["host"]."/".$l;
        }
        
        if (!in_array($l, $already_crawled)) {
            $already_crawled[] = $l;
            $crawling[] = $l;
            
            //Output the title, descriptions, keywords and URL. This output is
            //piped off to an external file using the command line
            //in my case: saved directly to the db table called index
            
            $details = json_decode(get_details($l));
            //print_r($details)."\n";
            
            //echo md5(@$details->URL)." "; //will echo the url hash due to md5 PHP function
            echo @$details->URL." >>_|_>> ";
            
            $rows = $pdo->query("SELECT * FROM `index` WHERE url_hash='".md5(@$details->URL)."'");
            $rows = $rows->fetchColumn();
            //echo $rows."\n";
            
            
            //This entire PDO Snippet does not insert records or update records in the DB. I have commented it out for future troubleshooting
            //I will use the mysqli_query method instead (using config.php for server details)
            /*
            $params = @array(':title' => $details->Title, ':description' => $details->Description, ':keywords' => $details->Keywords, ':url' => $details->URL, ':url_hash' => md5($details->URL));
            
            if($rows > 0) {
                //echo "UPDATE"."\n";
                if (!is_null($params[':title']) && !is_null($params[':description']) && $params[':title'] != '') {
                    //$result = $pdo->prepare("UPDATE `index` SET title=:title, description=:description, keywords=:keywords, url=:url, url_hash=:url_hash WHERE url_hash=:url_hash");
                    //$result = $result->execute($params);
                    
                    $sql = "UPDATE `index` SET `title`=:title, `description`=:description, `keywords`=:keywords, `url`=:url, `url_hash`=:url_hash WHERE `url_hash`=:url_hash";
                    $result = $pdo->exec($sql);
                }
                
            } else {
                //if the url hash is not found, insert the record/create a new record for the current link
                //echo "INSERT"."\n";
                
                if (!is_null($params[':title']) && !is_null($params[':description']) && $params[':title'] != '') {
                    //$result = $pdo->prepare("INSERT INTO `index` (`id`, `title`, `description`, `keywords`, `url`, `url_hash`) VALUES ('', :title, :description, :keywords, :url, :url_hash)");
                    //$result = $result->execute($params);
                    
                    $sql = "INSERT INTO `index` VALUES ('', :title, :description, :keywords, :url, :url_hash)"; //(`id`, `title`, `description`, `keywords`, `url`, `url_hash`)
                    $result = $pdo->exec($sql);
                }
                
            }*/
            
            $detailTitle = $details->Title;
            $detailDescription = $details->Description;
            $detailTypeTopic = $details->Type;
            $detailKeywords = $details->Keywords;
            $detailURL = $details->URL;
            $detailURLHash = md5($details->URL);
            $detailImageUrl = $details->Image;
            $detailFavicon = $details->Favicon;
            $detailContent = $details->Content;

            $date_now = date("Y-m-d H:i:s");

            $last_id = 0;

            if($rows > 0) { 
                $sql = "UPDATE `index` SET `title`='".clean($detailTitle)."', `description`='".clean($detailDescription)."', `type_topic` = '".clean($detailTypeTopic)."', `keywords`='".cleanKeywords($detailKeywords)."', `url`='$detailURL', `url_hash`='$detailURLHash', `image_url`='$detailImageUrl', `favicon`='$detailFavicon', `modified`='$date_now' WHERE `url_hash`='$detailURLHash'";
                
                if (mysqli_query( $db, $sql )) {
                    // update page content in the index_page_content table

                    echo "Link Updated: $detailURLHash \n\n";
                }else {
                    echo "Error: [$detailURLHash] - ".mysqli_error($db)."\n\n";
                }
            } else {
                $sql = "INSERT INTO `index` (`title`, `description`, `type_topic`, `keywords`, `url`, `url_hash`, `image_url`, `favicon`, `created`, `modified`) VALUES ('".clean($detailTitle)."', '".clean($detailDescription)."', '".clean($detailTypeTopic)."', '".cleanKeywords($detailKeywords)."', '$detailURL', '$detailURLHash', '$detailImageUrl', '$detailFavicon', '$date_now', '$date_now')"; //(`id`, `title`, `description`, `keywords`, `url`, `url_hash`)
                
                // $sql = "with new_parent as (
                //     INSERT into `index` (`title`, `description`, `type_topic`, `keywords`, `url`, `url_hash`, `image_url`, `favicon`, `created`, `modified`)
                //     VALUES ('".clean($detailTitle)."', '".clean($detailDescription)."', '".clean($detailTypeTopic)."', '".cleanKeywords($detailKeywords)."', '$detailURL', '$detailURLHash', '$detailImageUrl', '$detailFavicon', '$date_now', '$date_now')
                //     returning id; --<< this is the generated ID from parent_table
                //   )
                //   INSERT into `index_page_content` (`index_id`, `index_page_content`)
                //   SELECT id, '".$detailContent."'
                //   from new_parent;";

                if (mysqli_query( $db, $sql )) {
                    echo "New Link Saved: $detailURLHash \n\n";

                    // get last id
                    $last_id = $db->insert_id;

                    // clear mysqli_query


                    // save page content
                    $sql = "INSERT INTO `index_page_content` (`id`, `index_page_content`, `index_id`) VALUES (null, '$detailContent', '$last_id')";
                    if (mysqli_query( $db, $sql )) {
                        echo "Page Content Saved: $detailURLHash";
                    }
                }else {
                    echo "Error: [URLHash - $detailURLHash] - ".mysqli_error($db)."\n\n";
                }
            }
            
            //echo get_details($l);
        }
        
    }
    
    array_shift($crawling);
    foreach ($crawling as $site) {
        follow_links($site);
    }
    
}

follow_links($start);

//print_r($already_crawled)
