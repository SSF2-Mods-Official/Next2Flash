package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1478")]
   public dynamic class ItemDashAttack_82 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemDashAttack_82()
      {
         super();
         addFrameScript(0,this.frame1,5,this.frame6,7,this.frame8,23,this.frame24);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame6() : *
      {
         this.self.getItem().activateItem();
         this.self.attachEffect("global_dust_light",{"x":this.self.flipX(-7)});
      }
      
      internal function frame8() : *
      {
         this.self.getItem().deactivateItem();
      }
      
      internal function frame24() : *
      {
         this.self.endAttack();
      }
   }
}

