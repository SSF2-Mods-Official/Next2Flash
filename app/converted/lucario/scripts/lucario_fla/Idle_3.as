package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_3 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var rand:int;
        public var repeats:int;

        public function Idle_3()
        {
            super();
            addFrameScript(0, this.frame1, 42, this.frame43, 43, this.frame44, 85, this.frame86, 86, this.frame87, 119, this.frame120, 120, this.frame121, 123, this.frame124);
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

        public function checkBored():*
        {
            if ((this.repeats >= 3) && (SSF2API.random() > 0.5))
            {
                this.repeats = 0;
                if (SSF2API.random() > 0.5)
                {
                    this.self.stancePlayFrame("blink");
                }
                else
                {
                    this.self.stancePlayFrame("bored");
                };
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.rand = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
                this.checkBored();
            };
            if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
            };
        }

        internal function frame43():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame44():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame86():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame87():*
        {
            this.repeats++;
            this.self.updateAuraPaws();
        }

        internal function frame120():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame121():*
        {
            this.self.playSound("lucario_uncrouch");
        }

        internal function frame124():*
        {
            gotoAndStop("loop");
        }


    }
}

