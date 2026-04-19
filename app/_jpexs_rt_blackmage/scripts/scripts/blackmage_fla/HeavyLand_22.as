package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1325")]
   public dynamic class HeavyLand_22 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function HeavyLand_22()
      {
         super();
         addFrameScript(0,this.frame1,12,this.frame13);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(parent && SSF2API.isReady() && Boolean(this.self))
         {
            SSF2API.getCamera().shake(3);
            if(this.self.getMetalStatus())
            {
               this.self.playSound("metal_land_m");
            }
            else
            {
               this.self.playSound("blackmage_landHeavy");
            }
         }
      }
      
      internal function frame13() : *
      {
         this.self.endAttack();
      }
   }
}

