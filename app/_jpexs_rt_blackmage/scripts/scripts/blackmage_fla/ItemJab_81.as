package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1477")]
   public dynamic class ItemJab_81 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemJab_81()
      {
         super();
         addFrameScript(0,this.frame1,3,this.frame4,4,this.frame5,12,this.frame13);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame4() : *
      {
         this.self.getItem().activateItem();
         this.self.attachEffect("global_dust_light",{"x":this.self.flipX(-7)});
      }
      
      internal function frame5() : *
      {
         this.self.getItem().deactivateItem();
      }
      
      internal function frame13() : *
      {
         this.self.endAttack();
      }
   }
}

