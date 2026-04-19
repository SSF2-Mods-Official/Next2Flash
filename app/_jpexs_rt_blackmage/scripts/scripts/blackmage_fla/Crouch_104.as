package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1515")]
   public dynamic class Crouch_104 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Crouch_104()
      {
         super();
         addFrameScript(0,this.frame1,3,this.frame4,8,this.frame9);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame4() : *
      {
         this.self.setGlobalVariable("crouchdown",true);
      }
      
      internal function frame9() : *
      {
         this.self.stancePlayFrame("loop");
      }
   }
}

