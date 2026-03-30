package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_42 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function HeavyLand_42()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 13, this.frame14, 31, this.frame32, 35, this.frame36, 46, this.frame47, 63, this.frame64, 75, this.frame76);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                switch (this.self.getGlobalVariable("usedUpB"))
                {
                case "softland":
                this.self.setGlobalVariable("usedUpB", "none");
                this.self.stancePlayFrame("soft");
                break;
                case "hardland":
                this.self.setGlobalVariable("usedUpB", "none");
                this.self.stancePlayFrame("hard");
                break;
                case 2:
                default:
                this.self.setGlobalVariable("usedUpB", "none");
                SSF2API.getCamera().shake(5);
                this.self.playSound("metal_land_l");
                this.self.playSound("dedede_land");
                break;
                }
            };
        }

        internal function frame11():*
        {
            this.self.endAttack();
        }

        internal function frame14():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_uspec_fail");
            SSF2API.getCamera().shake(8);
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }

        internal function frame36():*
        {
            SSF2API.getCamera().shake(5);
            this.self.playSound("ssf2_snd_sfx_dedede_uspec_longfail_01");
        }

        internal function frame47():*
        {
            SSF2API.getCamera().shake(3);
            this.self.playSound("ssf2_snd_sfx_dedede_uspec_longfail_02");
        }

        internal function frame64():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l1");
            }
            else
            {
                this.self.playSound("dedede_step1");
                this.self.playSound("dedede_step2");
            };
        }

        internal function frame76():*
        {
            this.self.endAttack();
        }


    }
}

