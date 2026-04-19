package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1546")]
   public dynamic class Get_UpAttack_129 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Get_UpAttack_129()
      {
         super();
         addFrameScript(0,this.frame1,8,this.frame9,11,this.frame12,13,this.frame14,15,this.frame16,24,this.frame25);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:MovieClip = null;
         var _loc6_:BlackMageExt = null;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.setIntangibility(true);
         }
      }
      
      internal function frame9() : *
      {
         this.self.playAttackSound(1);
      }
      
      internal function frame12() : *
      {
         this.self.attachEffect("global_dust_swirl");
      }
      
      internal function frame14() : *
      {
         this.self.playAttackSound(2);
      }
      
      internal function frame16() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame25() : *
      {
         this.self.endAttack();
      }
   }
}

