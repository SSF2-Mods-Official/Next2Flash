package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeRoll_224 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function LedgeRoll_224()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 9, this.frame10, 18, this.frame19, 22, this.frame23, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_jump");
        }

        internal function frame10():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_runstart");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame23():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step01");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

