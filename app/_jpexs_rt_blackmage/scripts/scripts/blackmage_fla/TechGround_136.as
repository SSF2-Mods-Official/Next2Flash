package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1554")]
   public dynamic class TechGround_136 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function TechGround_136()
      {
         super();
         addFrameScript(0,this.frame1,10,this.frame11,13,this.frame14);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(SSF2API.isReady() && Boolean(this.self))
         {
            this.self.setIntangibility(true);
            this.self.setGlobalVariable("canStartRise",true);
            if(!this.self.getMetalStatus())
            {
               this.self.playSound("menumove",true);
            }
         }
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

