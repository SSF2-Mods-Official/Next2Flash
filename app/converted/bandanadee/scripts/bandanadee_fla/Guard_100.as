package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Guard_100 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Guard_100()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame3():*
        {
            stop();
        }

        internal function frame4():*
        {
            this.self.stancePlayFrame("pause");
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }


    }
}

