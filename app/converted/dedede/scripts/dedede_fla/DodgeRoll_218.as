package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class DodgeRoll_218 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function DodgeRoll_218()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 9, this.frame10, 11, this.frame12, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_heavy", {"scaleX":-1});
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame10():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame12():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_step02");
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

