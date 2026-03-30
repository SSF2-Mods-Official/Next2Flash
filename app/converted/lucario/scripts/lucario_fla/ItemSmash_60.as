package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemSmash_60 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var xframe:String;

        public function ItemSmash_60()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 16, this.frame17, 28, this.frame29, 38, this.frame39, 44, this.frame45, 45, this.frame46, 47, this.frame48, 49, this.frame50, 56, this.frame57, 59, this.frame60, 62, this.frame63, 65, this.frame66);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.self.updateAuraPaws();
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
            this.self.updateAuraPaws();
        }

        internal function frame17():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame29():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame39():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.updateAuraPaws();
        }

        internal function frame48():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            this.self.updateAuraPaws();
        }

        internal function frame50():*
        {
            this.self.getItem().deactivateItem();
            this.self.updateAttackStats({"chargetime_max":0});
            this.self.updateAuraPaws();
        }

        internal function frame57():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame60():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame63():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame66():*
        {
            this.self.endAttack();
        }


    }
}

