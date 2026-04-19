package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1479")]
   public dynamic class ItemTilt_83 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemTilt_83()
      {
         super();
         addFrameScript(0,this.frame1,6,this.frame7,8,this.frame9,18,this.frame19);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame7() : *
      {
         this.self.getItem().activateItem();
         this.self.attachEffect("global_dust_heavy",{
            "x":this.self.flipX(-7),
            "y":3,
            "scaleX":-0.5,
            "scaleY":-0.5
         });
      }
      
      internal function frame9() : *
      {
         this.self.getItem().deactivateItem();
      }
      
      internal function frame19() : *
      {
         this.self.endAttack();
      }
   }
}

