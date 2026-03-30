package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_89 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Crouch_89()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.playSound("bandanadee_crouch1");
            };
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame7():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

