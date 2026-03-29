package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class HangRoll_97 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function HangRoll_97()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 8, this.frame9, 12, this.frame13, 16, this.frame17, 18, this.frame19, 20, this.frame21, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("upSpecUsed", false);
                this.self.setGlobalVariable("nairUsed", false);
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("gw_jump1");
        }

        internal function frame9():*
        {
            this.self.playSound("gw_dash");
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("gw_step1");
            };
        }

        internal function frame17():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("gw_step2");
            };
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame21():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("gw_step1");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

