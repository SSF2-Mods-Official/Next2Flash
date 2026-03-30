package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Getup_95 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var ready:*;

        public function Getup_95()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 26, this.frame27, 28, this.frame29, 30, this.frame31, 31, this.frame32, 35, this.frame36, 36, this.frame37, 42, this.frame43, 46, this.frame47, 49, this.frame50);
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
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            SSF2API.getCamera().shake(3);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.ready = false;
                this.self.updateAuraPaws();
            };
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("lucario_land02");
                };
            };
        }

        internal function frame13():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("lucario_land01");
            };
        }

        internal function frame14():*
        {
            stop();
            this.ready = true;
            this.self.updateAuraPaws();
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
            this.self.updateAuraPaws();
        }

        internal function frame27():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame29():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }

        internal function frame32():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame36():*
        {
            if (this.self.getGlobalVariable("standloop") > 0)
            {
                gotoAndStop("standloop");
            };
        }

        internal function frame37():*
        {
            if (this.self.getGlobalVariable("standtime") > 0)
            {
                gotoAndStop("standloop");
                this.self.createTimer(1, -1, this.standCountdown);
            };
            this.self.updateAuraPaws();
        }

        internal function frame43():*
        {
            this.self.updateAuraPaws();
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("lucario_land1");
            };
        }

        internal function frame47():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("lucario_land01");
            };
        }

        internal function frame50():*
        {
            if (this.self.getState() == CState.CRASH_GETUP)
            {
                this.self.setState(CState.CRASH_LAND);
            };
            gotoAndStop("dead");
        }


    }
}

