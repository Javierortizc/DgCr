<head>
<meta charset="UTF-8" />
</head>
<?php
//get the q parameter from URL
$q=$_POST["q"];
if (strlen($q)<=5) { die; }
//if( strcmp( $_GET["mode"], 'like') == 0)    $busqueda=searchTermSnomedLike($conn, $q);
//if( strcmp( $_GET["mode"], 'nl')   == 0)    $busqueda=searchTermSnomed($conn, $q);
//print ("/usr/local/bin/python3 /Users/javierortiz/Desktop/DetectorPC/cliente.py \"".$q."\"");
exec("/usr/local/bin/python3 /Users/javierortiz/Desktop/DetectorPC/cliente.py \"".addslashes($q)."\" 2>&1", $output, $respuesta);

//output the response
#echo '<b>Esto es lo que envió:</b><br/>'.nl2br($q).'<br/>';
#echo '<b>Esto es lo que recivió:</b><br/>'.$output.'<br/>';

#print_r($output);

if ($respuesta==1) {
  echo "SERVIDOR APAGADO";
}
else {
  echo nl2br($output[0]);
};


?>
