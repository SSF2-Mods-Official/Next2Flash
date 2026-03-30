package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_3 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var rand:int;
        public var repeats:int;

        public function Idle_3()
        {
            super();
            addFrameScript(0, this.frame1, 32, this.frame33, 65, this.frame66, 129, this.frame130, 193, this.frame194, 197, this.frame198);
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
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.rand = ((SSF2API.random() * 2147483647) % 20);
                if (this.rand > 15)
                {
                    this.self.stancePlayFrame("blink");
                }
                else if (this.repeats >= 2)
                {
                    if (this.rand > 14)
                    {
                        this.repeats = 0;
                        this.self.stancePlayFrame("wait1");
                    }
                    else if (this.rand > 12)
                    {
                        this.repeats = 0;
                        this.self.stancePlayFrame("wait2");
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
            this.self.stancePlayFrame("loop");
        }

        internal function frame66():*
        {
            this.repeats++;
            this.self.stancePlayFrame("loop");
        }

        internal function frame130():*
        {
            this.repeats++;
            this.self.stancePlayFrame("loop");
        }

        internal function frame194():*
        {
            this.repeats++;
            this.self.stancePlayFrame("loop");
        }

        internal function frame198():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

