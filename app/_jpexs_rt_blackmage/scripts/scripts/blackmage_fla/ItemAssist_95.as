package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1491")]
   public dynamic class ItemAssist_95 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemAssist_95()
      {
         super();
         addFrameScript(0,this.frame1,7,this.frame8,30,this.frame31);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame8() : *
      {
         this.self.getItem().activateItem();
      }
      
      internal function frame31() : *
      {
         this.self.endAttack();
      }
   }
}

