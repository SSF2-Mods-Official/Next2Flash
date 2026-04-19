package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HangRoll_117 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function HangRoll_117()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 8, this.frame9, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (parent && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("bm_doublejump");
        }

        internal function frame9():*
        {
            this.self.playSound("run_start");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame20():*
        {
            this.self.playSound("blackmage_landLight");
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

