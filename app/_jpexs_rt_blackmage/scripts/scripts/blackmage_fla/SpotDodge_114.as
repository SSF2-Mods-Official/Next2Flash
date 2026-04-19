package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1529")]
   public dynamic class SpotDodge_114 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function SpotDodge_114()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,10,this.frame11,13,this.frame14);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame2() : *
      {
         this.self.attachEffect("bm_misstext",{
            "flip":false,
            "resize":false
         });
         this.self.setIntangibility(true);
         this.self.attachEffect("global_dust_cloud",{
            "scaleX":0.8,
            "scaleY":0.8
         });
      }
      
      internal function frame11() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame14() : *
      {
         this.self.endAttack();
      }
   }
}

