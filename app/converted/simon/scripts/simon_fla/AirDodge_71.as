package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class AirDodge_71 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function AirDodge_71()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 14, this.frame15, 23, this.frame24);
        }

        public function dodgeLand(_arg_1:*=null):*
        {
            this.self.toLand();
            this.self.stancePlayFrame("dodgeland");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.dodgeLand);
        }

        internal function frame15():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

