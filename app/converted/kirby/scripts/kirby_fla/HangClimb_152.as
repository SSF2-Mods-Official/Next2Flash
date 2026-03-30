package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class HangClimb_152 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function HangClimb_152()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 12, this.frame13, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame7():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame13():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-15});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step01");
            };
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

