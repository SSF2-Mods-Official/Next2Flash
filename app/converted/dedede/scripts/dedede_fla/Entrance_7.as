package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_7 extends MovieClip
    {

        public var deesDefault_B:MovieClip;
        public var deesDefault_F:MovieClip;
        public var deesMetal_B:MovieClip;
        public var deesMetal_F:MovieClip;
        public var deesMono_B:MovieClip;
        public var deesMono_F:MovieClip;
        public var deesRetro_B:MovieClip;
        public var deesRetro_F:MovieClip;
        public var deesShadow_B:MovieClip;
        public var deesShadow_F:MovieClip;
        public var itemBox:MovieClip;
        public var throneDefault_B:MovieClip;
        public var throneDefault_F:MovieClip;
        public var throneMetal_B:MovieClip;
        public var throneMetal_F:MovieClip;
        public var throneMono_B:MovieClip;
        public var throneMono_F:MovieClip;
        public var throneRetro_B:MovieClip;
        public var throneRetro_F:MovieClip;
        public var throneShadow_B:MovieClip;
        public var throneShadow_F:MovieClip;
        public var self:DededeExt;

        public function Entrance_7()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 14, this.frame15, 22, this.frame23, 25, this.frame26, 30, this.frame31, 34, this.frame35, 45, this.frame46);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.isMonoDedede())
                {
                    this.throneDefault_F.visible = false;
                    this.throneMono_F.visible = true;
                    this.throneShadow_F.visible = false;
                    this.throneRetro_F.visible = false;
                    this.throneMetal_F.visible = false;
                    this.throneDefault_B.visible = false;
                    this.throneMono_B.visible = true;
                    this.throneShadow_B.visible = false;
                    this.throneRetro_B.visible = false;
                    this.throneMetal_B.visible = false;
                    this.deesDefault_F.visible = false;
                    this.deesMono_F.visible = true;
                    this.deesShadow_F.visible = false;
                    this.deesRetro_F.visible = false;
                    this.deesMetal_F.visible = false;
                    this.deesDefault_B.visible = false;
                    this.deesMono_B.visible = true;
                    this.deesShadow_B.visible = false;
                    this.deesRetro_B.visible = false;
                    this.deesMetal_B.visible = false;
                }
                else if (this.self.isShadowDedede())
                {
                    this.throneDefault_F.visible = false;
                    this.throneMono_F.visible = false;
                    this.throneShadow_F.visible = true;
                    this.throneRetro_F.visible = false;
                    this.throneMetal_F.visible = false;
                    this.throneDefault_B.visible = false;
                    this.throneMono_B.visible = false;
                    this.throneShadow_B.visible = true;
                    this.throneRetro_B.visible = false;
                    this.throneMetal_B.visible = false;
                    this.deesDefault_F.visible = false;
                    this.deesMono_F.visible = false;
                    this.deesShadow_F.visible = true;
                    this.deesRetro_F.visible = false;
                    this.deesMetal_F.visible = false;
                    this.deesDefault_B.visible = false;
                    this.deesMono_B.visible = false;
                    this.deesShadow_B.visible = true;
                    this.deesRetro_B.visible = false;
                    this.deesMetal_B.visible = false;
                }
                else if (this.self.isRetroDedede())
                {
                    this.throneDefault_F.visible = false;
                    this.throneMono_F.visible = false;
                    this.throneShadow_F.visible = false;
                    this.throneRetro_F.visible = true;
                    this.throneMetal_F.visible = false;
                    this.throneDefault_B.visible = false;
                    this.throneMono_B.visible = false;
                    this.throneShadow_B.visible = false;
                    this.throneRetro_B.visible = true;
                    this.throneMetal_B.visible = false;
                    this.deesDefault_F.visible = false;
                    this.deesMono_F.visible = false;
                    this.deesShadow_F.visible = false;
                    this.deesRetro_F.visible = true;
                    this.deesMetal_F.visible = false;
                    this.deesDefault_B.visible = false;
                    this.deesMono_B.visible = false;
                    this.deesShadow_B.visible = false;
                    this.deesRetro_B.visible = true;
                    this.deesMetal_B.visible = false;
                }
                else if (this.self.isMetalDedede())
                {
                    this.throneDefault_F.visible = false;
                    this.throneMono_F.visible = false;
                    this.throneShadow_F.visible = false;
                    this.throneRetro_F.visible = false;
                    this.throneMetal_F.visible = true;
                    this.throneDefault_B.visible = false;
                    this.throneMono_B.visible = false;
                    this.throneShadow_B.visible = false;
                    this.throneRetro_B.visible = false;
                    this.throneMetal_B.visible = true;
                    this.deesDefault_F.visible = false;
                    this.deesMono_F.visible = false;
                    this.deesShadow_F.visible = false;
                    this.deesRetro_F.visible = false;
                    this.deesMetal_F.visible = true;
                    this.deesDefault_B.visible = false;
                    this.deesMono_B.visible = false;
                    this.deesShadow_B.visible = false;
                    this.deesRetro_B.visible = false;
                    this.deesMetal_B.visible = true;
                }
                else
                {
                    this.throneDefault_F.visible = true;
                    this.throneMono_F.visible = false;
                    this.throneShadow_F.visible = false;
                    this.throneRetro_F.visible = false;
                    this.throneMetal_F.visible = false;
                    this.throneDefault_B.visible = true;
                    this.throneMono_B.visible = false;
                    this.throneShadow_B.visible = false;
                    this.throneRetro_B.visible = false;
                    this.throneMetal_B.visible = false;
                    this.deesDefault_F.visible = true;
                    this.deesMono_F.visible = false;
                    this.deesShadow_F.visible = false;
                    this.deesRetro_F.visible = false;
                    this.deesMetal_F.visible = false;
                    this.deesDefault_B.visible = true;
                    this.deesMono_B.visible = false;
                    this.deesShadow_B.visible = false;
                    this.deesRetro_B.visible = false;
                    this.deesMetal_B.visible = false;
                };
            };
        }

        internal function frame6():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_entrance_dee_step01");
        }

        internal function frame15():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_entrance_dee_step02");
        }

        internal function frame23():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_entrance_dee_step01");
        }

        internal function frame26():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_entrance_chair");
        }

        internal function frame31():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_entrance_dee_exit");
        }

        internal function frame35():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(5);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_landHeavy");
                };
            };
        }

        internal function frame46():*
        {
            this.self.endAttack();
        }


    }
}

