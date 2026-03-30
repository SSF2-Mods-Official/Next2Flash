package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_idle_6 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var rand:int;
        public var repeats:int;
        public var target:*;
        public var random:*;

        public function bomberman_idle_6()
        {
            super();
            addFrameScript(0, this.frame1, 32, this.frame33, 104, this.frame105, 108, this.frame109);
        }

        public function uncrouch(_arg_1:*=null):*
        {
            if ((_arg_1.data.fromState == 12) && this.self.getGlobalVariable("crouchdown"))
            {
                this.self.setGlobalVariable("crouchdown", false);
                this.self.stancePlayFrame("uncrouch");
            }
            else
            {
                this.self.setGlobalVariable("crouchdown", false);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.rand = 0;
            if (!this.repeats)
            {
                this.repeats = 0;
            };
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.repeats >= 3)
                {
                    this.rand = SSF2API.randomInteger(0, 3);
                    if (this.rand >= 3)
                    {
                        this.repeats = 0;
                        gotoAndStop("idle");
                    };
                };
                if (this.self.getCPUTarget() != null)
                {
                    this.target = this.self.getCPUTarget();
                    this.random = (SSF2API.random() * 100);
                    if ((this.target == null) || (this.target.getX() > (this.self.getX() + 500)) || (this.target.getY() > (this.self.getY() + 500)) || (this.target.getX() < (this.self.getX() - 500)) || (this.target.getY() < (this.self.getY() - 500)) || this.target.inUpperLeftWarningBounds() || this.target.inUpperRightWarningBounds() || this.target.inLowerLeftWarningBounds() || this.target.inLowerRightWarningBounds())
                    {
                        if ((this.self.getCPUForcedAction() == -1) || (this.self.getCPUForcedAction() == 5))
                        {
                            if ((this.random >= 34) && (this.random <= 50))
                            {
                                this.self.importCPUControls([64, 1, 1024, 7]);
                            };
                            if ((this.random >= 17) && (this.random < 34))
                            {
                                this.self.importCPUControls([64, 31, 1024, 7]);
                            };
                            if ((this.random >= 0) && (this.random < 17))
                            {
                                this.self.importCPUControls([64, 55, 1024, 7]);
                            };
                        };
                    };
                };
            };
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame33():*
        {
            this.repeats++;
            gotoAndStop("loop");
        }

        internal function frame105():*
        {
            gotoAndStop("loop");
        }

        internal function frame109():*
        {
            gotoAndStop("loop");
        }


    }
}

