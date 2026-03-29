package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_40 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Skid_40()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
        }

        internal function frame2():*
        {
            this.self.playSound("cfalcon_dashstop");
        }

        internal function frame7():*
        {
            this.self.endAttack();
        }


    }
}

