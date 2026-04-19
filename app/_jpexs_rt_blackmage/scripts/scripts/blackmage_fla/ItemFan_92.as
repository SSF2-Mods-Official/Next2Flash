package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1488")]
   public dynamic class ItemFan_92 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemFan_92()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,3,this.frame4,5,this.frame6);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame3() : *
      {
         this.self.getItem().activateItem();
         this.self.playAttackSound(1);
         this.self.attachEffect("global_dust_light",{"x":this.self.flipX(-7)});
      }
      
      internal function frame4() : *
      {
         this.self.getItem().deactivateItem();
      }
      
      internal function frame6() : *
      {
         this.self.endAttack();
      }
   }
}

