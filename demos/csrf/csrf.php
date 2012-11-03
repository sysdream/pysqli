<?php
session_start();
?>

<html>
<head><title>Demo: blind sqli</title></head>
<body>

<?php
@mysql_connect("localhost","demo","demo");
@mysql_select_db("demo");

function generate_token()
{
    $_SESSION['token'] = md5(rand(11111,99999).'_'.md5($_SERVER['REMOTE_ADDR']).time());
}

if (!empty($_POST['id']) && !empty($_POST['token']))
{
    if ($_SESSION['token'] === $_POST['token'])
    {
        $sql = "SELECT * FROM demo WHERE id=".$_POST['id'];
        $res = @mysql_query($sql);
        if(@mysql_num_rows($res)!=1)
            echo("<b>Article inexistant</b><br/>");
        else
            echo("<b>Article existant mais impossible d'afficher</b><br/>");
    }
}

generate_token(); 

?>

<form action="" method="POST">
ID article: <input type="text" name="id" value="1"/><br/>
<input type="hidden" name="token" value="<?php echo($_SESSION['token']); ?>"/>
<input type="submit" value="OK"/>
</form>

</body>
</html>
