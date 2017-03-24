<?php

   // Commands
   $temp_cmd = 'temp';
   $erase_cmd = 'erase';
   $print_cmd = 'print';
   $graph_cmd = 'graph';

   // The data file
   $file = "data.csv";

   // The graph file
   $graph = "graph.png";

   // Add data to file
   if(strlen($_GET[$temp_cmd]) !== 0){
      if (file_exists($file)) {
         $fh = fopen($file, 'a');
      }else{
         $fh = fopen($file, 'w');
      }
      fwrite($fh, $_GET['temp']."\n");
      fclose($fh);
   }
   
   // Erase the file
   if(isset($_GET[$erase_cmd])){
      if (file_exists($file)) {
         unlink($file);
      }
   }

   // Print the file
   if(isset($_GET[$print_cmd])){
      if (file_exists($file)) {
         $homepage = file_get_contents($file);
         echo nl2br($homepage);
      } 
   }

   // Print the graph
   if(isset($_GET[$graph_cmd])){
      if (file_exists($file)) {
         include("pChart/pData.class"); 
         include("pChart/pChart.class"); 
         
         $bins = preg_split ('/$\R?^/m', file_get_contents($file)); 
         
         //Dataset definition      
         $DataSet = new pData;     
         $DataSet->AddPoint($bins,"Serie1");
         //$DataSet->ImportFromCSV($file,",",array(1),FALSE,0);     
         $DataSet->AddAllSeries();     
         $DataSet->SetAbsciseLabelSerie();          
         $DataSet->SetYAxisName("Visitors");   
         
         
         $Test = new pChart(700,230);     
         $Test->setFontProperties("pChart/tahoma.ttf",8);     
         $Test->setGraphArea(70,30,680,200);     
         $Test->drawFilledRoundedRectangle(7,7,693,223,5,240,240,240);     
         $Test->drawRoundedRectangle(5,5,695,225,5,230,230,230);     
         $Test->drawGraphArea(255,255,255,TRUE);  
         $Test->drawScale($DataSet->GetData(),$DataSet->GetDataDescription(),SCALE_NORMAL,150,150,150,TRUE,0,2);     
         $Test->drawGrid(4,TRUE,230,230,230,50);  
              
         $Test->setFontProperties("pChart/tahoma.ttf",6);     
         $Test->drawTreshold(0,143,55,72,TRUE,TRUE);     
          
         $Test->drawLineGraph($DataSet->GetData(),$DataSet->GetDataDescription());     
         $Test->drawPlotGraph($DataSet->GetData(),$DataSet->GetDataDescription(),3,2,255,255,255);     
              
         $Test->setFontProperties("pChart/tahoma.ttf",8);     
         $Test->drawLegend(75,35,$DataSet->GetDataDescription(),255,255,255);     
         $Test->setFontProperties("pChart/tahoma.ttf",10);     
         $Test->drawTitle(60,22,"Site Visitors",50,50,50,585);     
         $Test->Render($graph); 


         echo '<img src="';
         echo $graph;
         echo '"/>';
      }
   }
?>
