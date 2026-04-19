package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1531")]
   public dynamic class HangClimb_116 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function HangClimb_116()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,8,this.frame9,10,this.frame11,15,this.frame16,16,this.frame17);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.setIntangibility(true);
         }
      }
      
      internal function frame3() : *
      {
         this.self.playSound("bm_doublejump");
      }
      
      internal function frame9() : *
      {
         this.self.setXSpeed(4.5,false);
      }
      
      internal function frame11() : *
      {
         this.self.playSound("blackmage_landLight");
      }
      
      internal function frame16() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame17() : *
      {
         this.self.endAttack();
      }
   }
}

