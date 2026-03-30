package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_item_jab_54 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_item_jab_54()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame5():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}

