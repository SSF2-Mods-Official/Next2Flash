package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_Up_86 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var ready:*;

        public function Get_Up_86()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 26, this.frame27, 31, this.frame32, 36, this.frame37, 37, this.frame38, 47, this.frame48, 50, this.frame51);
        }

        public function standCountdown(_arg_1:*=null):*
        {
            if (this.self.getGlobalVariable("standtime") > 0)
            {
                this.self.setGlobalVariable("standtime", (this.self.getGlobalVariable("standtime") - 1));
            }
            else
            {
                this.self.destroyTimer(this.standCountdown);
                gotoAndStop("collapse");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.ready = false;
                SSF2API.getCamera().shake(4);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame13():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame14():*
        {
            stop();
            this.ready = true;
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("dead");
        }

        internal function frame16():*
        {
            if (!this.self.isForcedCrash())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame27():*
        {
            if (!this.self.isForcedCrash())
            {
                this.self.setIntangibility(false);
            };
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }

        internal function frame37():*
        {
            if (this.self.getGlobalVariable("standloop") > 0)
            {
                gotoAndStop("standloop");
            };
        }

        internal function frame38():*
        {
            if (this.self.getGlobalVariable("standtime") > 0)
            {
                gotoAndStop("standloop");
                this.self.createTimer(1, -1, this.standCountdown);
            };
        }

        internal function frame48():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("simon_land");
            };
        }

        internal function frame51():*
        {
            if (this.self.getState() == CState.CRASH_GETUP)
            {
                this.self.setState(CState.CRASH_LAND);
            };
            gotoAndStop("dead");
        }


    }
}

