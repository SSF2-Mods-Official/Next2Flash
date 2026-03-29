package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_145 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function ItemAssist_145()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
        }

        internal function frame8():*
        {
            if (this.self.getItem())
            {
                this.self.getItem().activateItem();
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

