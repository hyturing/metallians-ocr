function copy() {
  var Text = document.getElementById("txtbox");

  Text.select();

  navigator.clipboard.writeText(Text.value);
}
