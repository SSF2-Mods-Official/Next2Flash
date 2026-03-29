package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class EdgeLean_176 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var rand:int;

        public function EdgeLean_176()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 40, this.frame41);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
        }

        internal function frame2():*
        {
            this.rand = (10 * SSF2API.random());
            if ((this.rand >= 8) && !(this.self.getMetalStatus()))
            {
                this.self.playSound("cfalcon_otto", true);
            };
        }

        internal function frame41():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

