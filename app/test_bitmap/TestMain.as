package
{
   import flash.display.Sprite;
   import flash.display.Bitmap;
   import flash.display.BitmapData;
   import flash.text.TextField;
   import flash.text.TextFormat;
   
   [SWF(width="400", height="300", backgroundColor="#333333", frameRate="30")]
   public class TestMain extends Sprite
   {
      public function TestMain()
      {
         var log:TextField = new TextField();
         log.defaultTextFormat = new TextFormat("_sans", 12, 0xFFFFFF);
         log.width = 380;
         log.height = 280;
         log.x = 10;
         log.y = 10;
         log.multiline = true;
         log.wordWrap = true;
         addChild(log);
         
         var output:String = "";
         
         try
         {
            output += "=== bm_dairHand threshold() test ===\n\n";
            
            // Step 1: Instantiate
            var bmd:BitmapData = new bm_dairHand(0, 0);
            output += "1. new bm_dairHand(0,0) OK\n";
            output += "   width=" + bmd.width + " height=" + bmd.height + "\n";
            output += "   rect=" + bmd.rect + "\n";
            output += "   transparent=" + bmd.transparent + "\n";
            
            // Step 2: Check pixel
            try
            {
               var px:uint = bmd.getPixel32(0, 0);
               output += "2. getPixel32(0,0)=0x" + px.toString(16) + " OK\n";
            }
            catch (e2:Error)
            {
               output += "2. getPixel32 FAILED: " + e2.message + "\n";
            }
            
            // Step 3: threshold (the operation that crashes in the game)
            try
            {
               var dest:BitmapData = new BitmapData(bmd.width, bmd.height, true, 0x00000000);
               output += "3. dest BitmapData created OK\n";
               
               var count:uint = dest.threshold(
                  bmd,              // sourceBitmapData
                  bmd.rect,         // sourceRect
                  bmd.rect.topLeft, // destPoint
                  "==",             // operation
                  0xFF000000,       // threshold (black with full alpha)
                  0xFFFF0000,       // color (red replacement)
                  0xFF000000,       // mask
                  false             // copySource
               );
               output += "4. threshold() OK, matched " + count + " pixels\n";
            }
            catch (e3:Error)
            {
               output += "3-4. threshold FAILED: #" + e3.errorID + " " + e3.message + "\n";
            }
            
            // Step 4: Show the bitmap visually
            var bmp:Bitmap = new Bitmap(bmd);
            bmp.scaleX = bmp.scaleY = 10;
            bmp.x = 300;
            bmp.y = 10;
            addChild(bmp);
            output += "5. Bitmap displayed (10x scale at 300,10)\n";
            
            output += "\n=== ALL TESTS PASSED ===\n";
         }
         catch (e:Error)
         {
            output += "\nFATAL: #" + e.errorID + " " + e.message + "\n";
            output += e.getStackTrace() + "\n";
         }
         
         log.text = output;
         trace(output);
      }
   }
}
