// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_getupAttack_130

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_getupAttack_130 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_getupAttack_130()
        {
            addFrameScript(0, this.frame1, 5, this.frame6, 12, this.frame13, 15, this.frame16, 21, this.frame22, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
        }

        internal function frame13():*
        {
            this.self.refreshAttackID();
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame22():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

