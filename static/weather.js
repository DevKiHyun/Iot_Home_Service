function update_today_weather(master, data, success){
  var conditions = data["conditions"]["current_observation"];

  $('#weather_icon').attr('src', conditions["icon_url"]);
  $('#weather_conditions').html(conditions["weather"]);
  $('#weather_real').html(conditions["temp_c"]);
  $('#weather_feel').html('Feels like '+conditions["feelslike_c"]+'°C');
  $('#weather_wind_kph').html(conditions["wind_kph"]);
  $('#weather_wind_dir').html('kPh From '+ conditions["wind_dir"]);
  $('#pressure').html(conditions["pressure_mb"]+' hPa');
  $('#visibility').html(conditions["visibility_km"]+' km');
  $('#dewpoint').html(conditions["dewpoint_c"]+' °C');
  $('#humidity').html(conditions["relative_humidity"]);
}
