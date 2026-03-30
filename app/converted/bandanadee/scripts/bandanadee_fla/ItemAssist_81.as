package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_81 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function ItemAssist_81()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame8():*
        {
            this.self.getItem().activateItem();
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

