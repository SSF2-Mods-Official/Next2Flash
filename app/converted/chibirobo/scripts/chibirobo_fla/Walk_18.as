package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_18 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var playsound:Number;
        public var audio:Number;

        public function Walk_18()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame3():*
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

        internal function frame11():*
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


    }
}

