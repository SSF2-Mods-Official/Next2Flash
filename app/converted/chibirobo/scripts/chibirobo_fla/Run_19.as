package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_19 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var playsound:*;

        public function Run_19()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 13, this.frame14, 24, this.frame25, 26, this.frame27, 31, this.frame32);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.playsound = null;
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                this.self.playSound("run_start");
            };
        }

        internal function frame7():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame8():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.playsound = SSF2API.random();
                if ((this.playsound > 0) && (this.playsound <= 0.2))
                {
                    this.self.playSound("chibi_AStep");
                };
                if ((this.playsound > 0.2) && (this.playsound <= 0.4))
                {
                    this.self.playSound("chibi_BStep");
                };
                if ((this.playsound > 0.4) && (this.playsound <= 0.6))
                {
                    this.self.playSound("chibi_DStep");
                };
                if ((this.playsound > 0.6) && (this.playsound <= 0.8))
                {
                    this.self.playSound("chibi_EStep");
                };
                if ((this.playsound > 0.8) && (this.playsound <= 1))
                {
                    this.self.playSound("chibi_GStep");
                };
            };
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.playsound = SSF2API.random();
                if ((this.playsound > 0) && (this.playsound <= 0.2))
                {
                    this.self.playSound("chibi_AStep");
                };
                if ((this.playsound > 0.2) && (this.playsound <= 0.4))
                {
                    this.self.playSound("chibi_BStep");
                };
                if ((this.playsound > 0.4) && (this.playsound <= 0.6))
                {
                    this.self.playSound("chibi_DStep");
                };
                if ((this.playsound > 0.6) && (this.playsound <= 0.8))
                {
                    this.self.playSound("chibi_EStep");
                };
                if ((this.playsound > 0.8) && (this.playsound <= 1))
                {
                    this.self.playSound("chibi_GStep");
                };
            };
        }

        internal function frame25():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame27():*
        {
            this.self.playSound("chibi_Turn");
        }

        internal function frame32():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

